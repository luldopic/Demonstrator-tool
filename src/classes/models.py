from django.db import models, transaction
from users.models import Lecturer, Demonstrator, UserAvailability
from timetable.models import Semester, Timeslot
from django.db.models.signals import pre_save ,post_save
from django.dispatch import receiver

class Module(models.Model):
    """The `Module` model represents an academic module within the system. It includes details about the module such as 
    the class code, name, assigned lecturer, and the semester it belongs to.

    :param class_code: A unique identifier for the module.
    :type class_code: CharField
    :param name: The name of the module.
    :type name: CharField
    :param lecturer: A foreign key linking the module to a `Lecturer`. This field can be null if no lecturer is assigned.
    :type lecturer: ForeignKey
    :param semester: A foreign key linking the module to a `Semester`.
    :type semester: ForeignKey
    """
    class_code = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=100)
    lecturer = models.ForeignKey(Lecturer, null=True, blank=True, on_delete=models.SET_NULL)
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT, default=0)
    
    def formatted_lecturer_name(self):
        """Return the full name of the assigned lecturer, or a default message if no lecturer is assigned.

        :return: The lecturer's full name or a default message.
        :rtype: str
        """
        if self.lecturer is None:
            return "No lecturer assigned"
        return f"{self.lecturer.get_first_name()} {self.lecturer.get_last_name()}"
    formatted_lecturer_name.short_description = "Lecturer"
    
    def formatted_semester(self):
        """Return a formatted string of the semester's year and display name.

        :return: The formatted semester string.
        :rtype: str
        """
        return f"{self.semester.year} {self.semester.get_semester_display()}"
    formatted_semester.short_description = "Semester"
    
    def get_session_types(self):
        """Return a tuple indicating the types of sessions (Lecture, Tutorial, Lab, Other) associated with the module.

        :return: A tuple indicating the presence of each session type.
        :rtype: tuple
        """
        sessions = ModuleSession.objects.filter(class_code=self)
        session_type = [False, False, False, False]
        for session in sessions:
            if session.session_type == "Lecture":
                session_type[0] = True
            elif session.session_type == "Tutorial":
                session_type[1] = True
            elif session.session_type == "Lab":
                session_type[2] = True
            else:
                session_type[3] = True
        return tuple(session_type)
    
    def get_schedule(self):
        """Retrieve the schedule for the module, listing all session types and their associated timeslots.

        :return: A list of dictionaries containing session types and timeslots.
        :rtype: list of dict
        """
        sessions = ModuleSession.objects.filter(class_code=self)
        schedules = SessionSchedule.objects.filter(class_session__in=sessions).select_related("timeslot")
        
        all_schedules = []
        for schedule in schedules:
            all_schedules.append({
                'session_type': schedule.class_session.session_type,
                'timeslot': schedule.timeslot
            })
        
        return all_schedules
    
    def has_conflict(self):
        """Check if the module has any scheduling conflicts among its sessions.

        :return: `True` if there is a conflict, `False` otherwise.
        :rtype: bool
        """
        schedules = self.get_schedule()
        occupied_timeslot = []
        for schedule in schedules:
            if schedule["timeslot"] not in occupied_timeslot:
                occupied_timeslot.append(schedule["timeslot"])
            else:
                return True
        return False
    
    def count_sessions(self):
        """Count the number of session types and timeslots used by the module.

        :return: A tuple containing the count of session types and timeslots.
        :rtype: tuple
        """
        sessions = ModuleSession.objects.filter(class_code=self)
        schedules = self.get_schedule()
        return len(sessions), len(schedules)
    
    def update_lecturer_availability(self):
        """Update the availability of the lecturer based on the module's timeslots.

        :return: None
        """
        if self.lecturer:
            timeslots = Timeslot.objects.filter(sessionschedule__class_session__class_code=self)
            for timeslot in timeslots:
                availability, created = UserAvailability.objects.get_or_create(user = self.lecturer.user, timeslot = timeslot)
                availability.is_available = False
                availability.save()
    
    def __str__(self) -> str:
        """Return a string representation of the module, typically used in the Django admin interface.

        :return: The string representation of the module.
        :rtype: str
        """
        return super().__str__()
        

class ModuleSession(models.Model):
    """The `ModuleSession` model represents a specific session within a module, such as a lecture, tutorial, or lab.

    :param class_code: A foreign key linking the session to a `Module`.
    :type class_code: ForeignKey
    :param session_type: A string representing the type of session (e.g., Lecture, Tutorial, Lab).
    :type session_type: CharField
    :param required_demonstrator: The number of demonstrators required for the session.
    :type required_demonstrator: IntegerField
    :param test_session: A boolean indicating whether this is a test session.
    :type test_session: BooleanField
    """
    class_code = models.ForeignKey(Module, on_delete=models.PROTECT)
    session_type = models.CharField(max_length=40)
    required_demonstrator = models.IntegerField(default=0)
    test_session = models.BooleanField(default=False)
    
    def get_class_code(self):
        """Return the class code associated with the session.

        :return: The class code.
        :rtype: str
        """
        return self.class_code.class_code
    
    def get_timeslots(self):
        """Retrieve the timeslots associated with the session.

        :return: A queryset of timeslots.
        :rtype: QuerySet
        """
        return Timeslot.objects.filter(sessionschedule__class_session = self)
    
    def __str__(self) -> str:
        """Return a string representation of the module session, typically used in the Django admin interface.

        :return: The string representation of the module session.
        :rtype: str
        """
        return super().__str__()
    
    def save(self, *args, **kwargs):
        """Override the save method to ensure correct allocation of demonstrators based on the session requirements.

        :return: None
        """
        super(ModuleSession, self).save(*args, **kwargs)
        self.ensure_correct_allocation()
    
    def ensure_correct_allocation(self):
        """Ensure the correct number of allocations (demonstrators) are assigned to the session.

        :return: None
        """
        from allocations.models import Allocation
        current_allocations = Allocation.objects.filter(class_session=self)
        current_count = current_allocations.count()
        required_count = self.required_demonstrator
        
        if current_count < required_count:
            allocations_to_create = required_count - current_count
            allocations = [Allocation(class_session=self) for _ in range(allocations_to_create)]
            Allocation.objects.bulk_create(allocations)
        elif current_count > required_count:
            allocations_to_delete = current_allocations[:current_count - required_count]
            Allocation.objects.filter(id__in=[alloc.id for alloc in allocations_to_delete]).delete()
    

class SkillManager(models.Manager):
    """The `SkillManager` class provides custom manager methods for the `Skill` model, particularly for creating skills 
    across all levels (Beginner, Intermediate, Expert) with a single method call.

    :param create: Method to create a skill with all levels.
    :type create: Method
    """
    def create(self, name, **kwargs):
        """Create a skill across all levels (Beginner, Intermediate, Expert).

        :param name: The name of the skill.
        :type name: str
        :return: A list of created `Skill` objects, one for each level.
        :rtype: list
        """
        if not name:
            raise ValueError("The name field is required")
        
        with transaction.atomic():
            skills = []
            for level, _ in Skill.LEVEL_CHOICES:
                skill = super().create(name=name, level=level, **kwargs)
                skills.append(skill)
            return skills

class Skill(models.Model):
    """The `Skill` model represents a specific skill at a certain level, such as Beginner, Intermediate, or Expert.

    :param LEVEL_CHOICES: A list of tuples representing the different skill levels.
    :type LEVEL_CHOICES: list of tuple
    :param name: The name of the skill.
    :type name: CharField
    :param level: The skill level (0=Beginner, 1=Intermediate, 2=Expert).
    :type level: IntegerField
    """
    LEVEL_CHOICES = [
        (0, "Beginner"),
        (1, "Intermediate"),
        (2, "Expert")
    ]
    name = models.CharField(max_length=100)
    level = models.IntegerField(choices=LEVEL_CHOICES)
    
    objects = SkillManager()
    
    class Meta:
        unique_together = ["name", "level"]
    
    def __str__(self):
        """Return a string representation of the skill, including its name and level.

        :return: The string representation of the skill.
        :rtype: str
        """
        return f"Skill({self.name},{self.get_level_display()})"


class RequirementSkill(models.Model):
    """The `RequirementSkill` model represents a required skill for a specific module session.

    :param class_session: A foreign key linking the requirement to a `ModuleSession`.
    :type class_session: ForeignKey
    :param skill: A foreign key linking the requirement to a `Skill`.
    :type skill: ForeignKey
    """
    class_session = models.ForeignKey(ModuleSession, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT)
    
    class Meta:
        unique_together = ("class_session", "skill")
        
    def save(self, *args, **kwargs):
        """Override the save method to ensure the required skill is correctly linked or created.

        :return: None
        """
        if not self.skill_id:
            skill, created = Skill.objects.get_or_create(
                name=self.skill.name,
                level=self.skill.level
            )
            self.skill = skill
        super(RequirementSkill, self).save(*args, **kwargs)
        
    def __str__(self) -> str:
        """Return a string representation of the requirement skill, typically used in the Django admin interface.

        :return: The string representation of the requirement skill.
        :rtype: str
        """
        return super().__str__()

class SessionSchedule(models.Model):
    """The `SessionSchedule` model represents the schedule for a specific session, linking a module session to a timeslot.

    :param class_session: A foreign key linking the schedule to a `ModuleSession`.
    :type class_session: ForeignKey
    :param timeslot: A foreign key linking the schedule to a `Timeslot`.
    :type timeslot: ForeignKey
    """
    class_session = models.ForeignKey(ModuleSession, on_delete=models.CASCADE)
    timeslot = models.ForeignKey(Timeslot, on_delete=models.PROTECT)
    
    class Meta:
        unique_together = ("class_session", "timeslot")
    
class Competency(models.Model):
    """The `Competency` model represents the competency of a demonstrator in a specific skill.

    :param skill: A foreign key linking the competency to a `Skill`.
    :type skill: ForeignKey
    :param demonstrator: A foreign key linking the competency to a `Demonstrator`.
    :type demonstrator: ForeignKey
    """
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    demonstrator = models.ForeignKey(Demonstrator, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = "Competencies"
        unique_together = ["skill", "demonstrator"]
    
    def __str__(self) -> str:
        """Return a string representation of the competency, typically used in the Django admin interface.

        :return: The string representation of the competency.
        :rtype: str
        """
        return super().__str__()
        

@receiver(pre_save, sender=Module)
def update_lecturer_availability_before_module_save(sender, instance, **kwargs):
    """Signal receiver that updates the lecturer's availability before saving a module.

    :param sender: The model class that sent the signal, in this case, `Module`.
    :type sender: Model
    :param instance: The actual instance of `Module` that is being saved.
    :type instance: Module
    :param kwargs: Additional arguments passed to the signal handler.
    :type kwargs: dict
    :return: None
    """
    if instance.lecturer is None:
        return
    
    if instance.pk is not None: 
        try:
            previous_instance = Module.objects.get(pk=instance.pk)
            if previous_instance.lecturer != instance.lecturer:
                if previous_instance.lecturer:
                    previous_timeslots = Timeslot.objects.filter(sessionschedule__class_session__class_code=previous_instance)
                    for timeslot in previous_timeslots:
                        availability = UserAvailability.objects.get_or_create(user=previous_instance.lecturer.user, timeslot=timeslot)
                        if availability:
                            availability.is_available = True
                            availability.save()
        except Module.DoesNotExist:
            pass

@receiver(post_save, sender=Module)
def update_lecturer_availability_after_module_save(sender, instance, **kwargs):
    """Signal receiver that updates the lecturer's availability after saving a module.

    :param sender: The model class that sent the signal, in this case, `Module`.
    :type sender: Model
    :param instance: The actual instance of `Module` that is being saved.
    :type instance: Module
    :param kwargs: Additional arguments passed to the signal handler.
    :type kwargs: dict
    :return: None
    """
    if instance.lecturer is None:
        return
    instance.update_lecturer_availability()