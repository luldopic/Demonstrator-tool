from django.db import models
from timetable.models import Timeslot
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserManager(BaseUserManager):
    """
    Custom manager for the `User` model to overload certain functionalities.

    :param BaseUserManager: Django's base manager for user models.
    :type BaseUserManager: BaseUserManager
    """
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Create and return a superuser with the given username, email, and password.

        :param username: The username for the superuser.
        :type username: str
        :param email: The email address for the superuser.
        :type email: str
        :param password: The password for the superuser.
        :type password: str, optional
        :param extra_fields: Additional fields for the superuser.
        :type extra_fields: dict
        :raises ValueError: If `is_staff` or `is_superuser` is not set to True.
        :return: The created superuser.
        :rtype: User
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_lecturer', False)  # Set this based on your requirements
        extra_fields.setdefault('is_demonstrator', False)  # Set this based on your requirements

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser. Adds additional fields and methods.

    :param is_demonstrator: Indicates if the user is a demonstrator.
    :type is_demonstrator: bool
    :param is_lecturer: Indicates if the user is a lecturer.
    :type is_lecturer: bool
    :param is_fake: Indicates if the user is a fake user.
    :type is_fake: bool
    :param first_name: The first name of the user.
    :type first_name: str
    :param last_name: The last name of the user.
    :type last_name: str
    :param email: The email address of the user.
    :type email: str
    """
    is_demonstrator = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    is_fake = models.BooleanField(default=False)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    
    
    def __str__(self) -> str:
        """
        Return a string representation of the user.

        :return: A string representing the user, including their roles.
        :rtype: str
        """
        return f"User({self.username}, {self.first_name}, {self.last_name}, Lecturer: {self.is_lecturer}, Demonstrator: {self.is_demonstrator})"


    def is_available(self,timeslot):
        """
        Check if the user is available for the given timeslot.

        :param timeslot: The timeslot to check availability for.
        :type timeslot: Timeslot
        :return: True if the user is available, False otherwise.
        :rtype: bool
        """
        availability_slot = UserAvailability.objects.get(user=self, timeslot=timeslot)
        return availability_slot.is_available

class Role(models.Model):
    """
    Abstract base model representing a role associated with a user.

    :param user: A one-to-one relationship to the User model.
    :type user: ForeignKey
    """
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                primary_key=True)
    
    class Meta:
        abstract = True
    
    def get_first_name(self):
        """
        Return the first name of the user associated with the role.

        :return: The user's first name.
        :rtype: str
        """
        return self.user.first_name
    
    def get_last_name(self):
        """
        Return the last name of the user associated with the role.

        :return: The user's last name.
        :rtype: str
        """
        return self.user.last_name
    
    def is_available(self, timeslot):
        """
        Check if the user associated with the role is available for the given timeslot.

        :param timeslot: The timeslot to check availability for.
        :type timeslot: Timeslot
        :return: True if the user is available, False otherwise.
        :rtype: bool
        """
        return self.user.is_available(timeslot)
    
    def __str__(self) -> str:
        """
        Return a string representation of the role, typically the user's name.

        :return: The user's full name.
        :rtype: str
        """
        return f"{self.user.first_name} {self.user.last_name}"


class Demonstrator(Role):
    """
    Model representing a Demonstrator role associated with a user.
    """
    def __str__(self) -> str:
        """
        Return a string representation of the demonstrator, typically the demonstrator's name.

        :return: The user's full name.
        :rtype: str
        """
        return f"Demonstrator({self.user.first_name} {self.user.last_name})"
    
    

class Lecturer(Role):
    """
    Model representing a Lecturer role associated with a user.

    :param department: The department the lecturer belongs to.
    :type department: str
    """
    department = models.CharField(max_length=100)
    
    def __str__(self) -> str:
        """
        Return a string representation of the lecturer.

        :return: The user's full name.
        :rtype: str
        """
        return f"Lecturer({self.user.first_name} {self.user.last_name}, Department: {self.department})"


class UserAvailability(models.Model):
    """
    Model representing the availability of a user for a specific timeslot.

    :param user: A foreign key linking to the User model.
    :type user: ForeignKey
    :param timeslot: A foreign key linking to the Timeslot model.
    :type timeslot: ForeignKey
    :param is_available: Indicates whether the user is available for the timeslot.
    :type is_available: bool
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timeslot = models.ForeignKey(Timeslot, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "User Availability"
        unique_together = ["user", "timeslot"]
        
    def __str__(self) -> str:
        """
        Return a string representation of the user's availability for a specific timeslot.

        :return: A string representing the user's availability.
        :rtype: str
        """
        return f"UserAvailability(User: {self.user.username}, Timeslot: {self.timeslot}, Available: {self.is_available})"

@receiver(post_save, sender=User)
def add_lecdem_when_user_create(sender, instance, created, **kwargs):
    """
    Signal receiver to automatically create a Lecturer or Demonstrator role 
    when a new User is created, based on the user's roles.

    :param sender: The model class sending the signal.
    :type sender: Model
    :param instance: The instance of the User being saved.
    :type instance: User
    :param created: Indicates whether the User was created (True) or updated (False).
    :type created: bool
    :param kwargs: Additional keyword arguments.
    :type kwargs: dict
    """
    if created and instance.is_lecturer:
        Lecturer.objects.create(user=instance)
    if created and instance.is_demonstrator:
        Demonstrator.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_lecdem_when_user_saved(sender, instance, created, **kwargs):
    """
    Signal receiver to ensure the associated Lecturer or Demonstrator role is saved 
    when a User is saved.

    :param sender: The model class sending the signal.
    :type sender: Model
    :param instance: The instance of the User being saved.
    :type instance: User
    :param created: Indicates whether the User was created (True) or updated (False).
    :type created: bool
    :param kwargs: Additional keyword arguments.
    :type kwargs: dict
    """
    if instance.is_lecturer:
       Lecturer.objects.get_or_create(user=instance)
    if instance.is_demonstrator:
        Demonstrator.objects.get_or_create(user=instance)


@receiver(post_save, sender = User)
def create_blank_timetable(sender, instance, created, **kwargs):
    """
    Signal receiver to create a blank availability timetable for a new User 
    when the User is created.

    :param sender: The model class sending the signal.
    :type sender: Model
    :param instance: The instance of the User being saved.
    :type instance: User
    :param created: Indicates whether the User was created (True) or updated (False).
    :type created: bool
    :param kwargs: Additional keyword arguments.
    :type kwargs: dict
    """
    if created:
        timeslots = Timeslot.objects.all()
        for slot in timeslots:
            UserAvailability.objects.get_or_create(user=instance, timeslot=slot)
