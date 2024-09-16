import tests
from django.test import TestCase
from unittest.mock import patch, MagicMock
from users.models import User, Demonstrator, Lecturer, UserAvailability, Role
from timetable.models import Timeslot
from django.db.utils import IntegrityError



class UserModelTest(TestCase):
    """The `UserModelTest` class contains test cases for the `User` model in the Django application.

    :param setUp: Initializes the test environment, creating instances of `User` and `Timeslot`.
    :type setUp: Method
    :param test_create_user: Tests the creation of a `User` instance and verifies that it is saved correctly.
    :type test_create_user: Method
    :param test_str: Tests the `__str__` method to ensure it returns the correct string representation of the `User`.
    :type test_str: Method
    :param test_is_available: Tests the `is_available` method to ensure it correctly identifies if the user is available for a given timeslot.
    :type test_is_available: Method
    :param test_fake_user: Tests the `is_fake` field to ensure it correctly marks a user as fake.
    :type test_fake_user: Method
    :param test_unique_email: Tests the unique constraint on the `email` field to ensure duplicate emails cannot be created.
    :type test_unique_email: Method
    """
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        self.timeslot1 = Timeslot.objects.create(day=0, start_time="09:00", end_time="10:00")
        self.timeslot2 = Timeslot.objects.create(day=0, start_time="10:00", end_time="11:00")
        self.timeslot3 = Timeslot.objects.create(day=1, start_time="09:00", end_time="10:00")
        UserAvailability.objects.create(user=self.user, timeslot=self.timeslot1, is_available=True)
        UserAvailability.objects.create(user=self.user, timeslot=self.timeslot2, is_available=False)
    
    def test_create_user(self):
        self.assertIsNotNone(self.user.pk)
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertTrue(self.user.check_password('password123'))

    def test_str(self):
        self.user.first_name = 'Test'
        self.user.last_name = 'User'
        self.user.is_lecturer = True
        expected_str = "User(testuser, Test, User, Lecturer: True, Demonstrator: False)"
        self.assertEqual(str(self.user), expected_str)

    def test_is_available(self):
        # Test case where the user is available for a given timeslot
        self.assertTrue(self.user.is_available(self.timeslot1))
        
        # Test case where the user is not available for a given timeslot
        self.assertFalse(self.user.is_available(self.timeslot2))
        
        # Test case where no availability record exists for the given timeslot
        with self.assertRaises(UserAvailability.DoesNotExist):
            self.user.is_available(self.timeslot3)
    
    def test_fake_user(self):
        self.user.is_fake = True
        self.user.save()
        self.assertTrue(self.user.is_fake)

    def test_unique_email(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username='user2', email='testuser@example.com', password='password123')

    
class DemonstratorModelTest(TestCase):
    """The `DemonstratorModelTest` class contains test cases for the `Demonstrator` model in the Django application.

    :param setUp: Initializes the test environment, creating instances of `User` and `Demonstrator`.
    :type setUp: Method
    :param test_get_first_name: Tests the `get_first_name` method to ensure it returns the correct first name of the demonstrator.
    :type test_get_first_name: Method
    :param test_get_last_name: Tests the `get_last_name` method to ensure it returns the correct last name of the demonstrator.
    :type test_get_last_name: Method
    :param test_is_available: Tests the `is_available` method to ensure it correctly identifies if the demonstrator is available for a given timeslot.
    :type test_is_available: Method
    :param test_create_demonstrator_from_user: Tests the creation of a `Demonstrator` instance from a `User` and verifies that it is associated correctly.
    :type test_create_demonstrator_from_user: Method
    :param test_assign_user_demonstrator_role: Tests the assignment of the demonstrator role to a user.
    :type test_assign_user_demonstrator_role: Method
    :param test_delete_demonstrator: Tests the deletion of a demonstrator and ensures that the role is removed from the user.
    :type test_delete_demonstrator: Method
    :param test_remove_demonstrator_role_from_user: Tests the removal of the demonstrator role from a user.
    :type test_remove_demonstrator_role_from_user: Method
    """
    def setUp(self):
        self.user = User.objects.create_user(username='demonstratoruser', first_name='Demonstrator', last_name='Tester')
        self.demonstrator = Demonstrator.objects.create(user = self.user)
        
    def test_get_first_name(self):
        self.assertEqual(self.demonstrator.get_first_name(), 'Demonstrator')

    def test_get_last_name(self):
        self.assertEqual(self.demonstrator.get_last_name(), 'Tester')

    def test_is_available(self):
        self.timeslot = Timeslot.objects.create(day=1, start_time="09:00", end_time="10:00")
        UserAvailability.objects.create(user=self.user, timeslot=self.timeslot, is_available=True)
        self.assertTrue(self.demonstrator.is_available(self.timeslot))

    def test_create_demonstrator_from_user(self):
        self.assertEqual(self.demonstrator.user, self.user)

    def test_assign_user_demonstrator_role(self):
        self.user.is_demonstrator = True
        self.user.save()
        self.assertTrue(Demonstrator.objects.filter(user=self.user).exists())

    def test_delete_demonstrator(self):
        self.demonstrator.delete()
        self.assertFalse(Demonstrator.objects.filter(user=self.user).exists())

    def test_remove_demonstrator_role_from_user(self):
        self.user.is_demonstrator = True
        self.user.save()
        self.user.is_demonstrator = False
        self.user.save()
        self.assertFalse(Demonstrator.objects.filter(user=self.user).exists())

class LecturerModelTest(TestCase):
    """The `LecturerModelTest` class contains test cases for the `Lecturer` model in the Django application.

    :param setUp: Initializes the test environment, creating instances of `User` and `Lecturer`.
    :type setUp: Method
    :param test_get_first_name: Tests the `get_first_name` method to ensure it returns the correct first name of the lecturer.
    :type test_get_first_name: Method
    :param test_get_last_name: Tests the `get_last_name` method to ensure it returns the correct last name of the lecturer.
    :type test_get_last_name: Method
    :param test_is_available: Tests the `is_available` method to ensure it correctly identifies if the lecturer is available for a given timeslot.
    :type test_is_available: Method
    :param test_create_lecturer_from_user: Tests the creation of a `Lecturer` instance from a `User` and verifies that it is associated correctly.
    :type test_create_lecturer_from_user: Method
    :param test_assign_user_lecturer_role: Tests the assignment of the lecturer role to a user.
    :type test_assign_user_lecturer_role: Method
    :param test_delete_lecturer: Tests the deletion of a lecturer and ensures that the role is removed from the user.
    :type test_delete_lecturer: Method
    :param test_remove_lecturer_role_from_user: Tests the removal of the lecturer role from a user.
    :type test_remove_lecturer_role_from_user: Method
    """
    def setUp(self):
        self.user = User.objects.create_user(username='lectureruser', first_name='Lecturer', last_name='Tester')
        self.lecturer = Lecturer.objects.create(user = self.user, department='Maths')
    
    def test_get_first_name(self):
        self.assertEqual(self.lecturer.get_first_name(), 'Lecturer')

    def test_get_last_name(self):
        self.assertEqual(self.lecturer.get_last_name(), 'Tester')

    def test_is_available(self):
        self.timeslot = Timeslot.objects.create(day=1, start_time="09:00", end_time="10:00")
        UserAvailability.objects.create(user=self.user, timeslot=self.timeslot, is_available=True)
        self.assertTrue(self.lecturer.is_available(self.timeslot))

    def test_create_lecturer_from_user(self):
        self.assertEqual(self.lecturer.user, self.user)
        self.assertEqual(self.lecturer.department, 'Maths')

    def test_assign_user_lecturer_role(self):
        self.user.is_lecturer = True
        self.user.save()
        self.assertTrue(Lecturer.objects.filter(user=self.user).exists())

    def test_delete_lecturer(self):
        self.lecturer.delete()
        self.assertFalse(Lecturer.objects.filter(user=self.user).exists())

    def test_remove_lecturer_role_from_user(self):
        self.user.is_lecturer = True
        self.user.save()
        self.user.is_lecturer = False
        self.user.save()
        self.assertFalse(Lecturer.objects.filter(user=self.user).exists())

class UserAvailabilityModelTest(TestCase):
    """The `UserAvailabilityModelTest` class contains test cases for the `UserAvailability` model in the Django application.

    :param setUp: Initializes the test environment, creating instances of `User`, `Timeslot`, and `UserAvailability`.
    :type setUp: Method
    :param test_create_user_availability: Tests the creation of a `UserAvailability` instance and verifies that it is saved correctly.
    :type test_create_user_availability: Method
    :param test_availability_status: Tests the `is_available` field to ensure it correctly reflects the availability status of the user.
    :type test_availability_status: Method
    :param test_unique_together: Tests the unique constraint on the `user` and `timeslot` fields to ensure duplicate availabilities cannot be created.
    :type test_unique_together: Method
    :param test_user_deletion: Tests the behavior when the associated user is deleted, ensuring the availability record is also deleted.
    :type test_user_deletion: Method
    :param test_timeslot_deletion: Tests the behavior when the associated timeslot is deleted, ensuring the availability record is also deleted.
    :type test_timeslot_deletion: Method
    """
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        self.timeslot = Timeslot.objects.create(day=0, start_time="09:00", end_time="10:00")

    def test_create_user_availability(self):
        availability = UserAvailability.objects.create(user=self.user, timeslot=self.timeslot, is_available=True)
        self.assertTrue(availability.is_available)

    def test_availability_status(self):
        availability = UserAvailability.objects.create(user=self.user, timeslot=self.timeslot, is_available=True)
        self.assertTrue(availability.is_available)
        availability.is_available = False
        availability.save()
        self.assertFalse(availability.is_available)

    def test_unique_together(self):
        UserAvailability.objects.create(user=self.user, timeslot=self.timeslot)
        with self.assertRaises(IntegrityError):
            UserAvailability.objects.create(user=self.user, timeslot=self.timeslot)

    def test_user_deletion(self):
        availability = UserAvailability.objects.create(user=self.user, timeslot=self.timeslot)
        self.user.delete()
        self.assertFalse(UserAvailability.objects.filter(pk=availability.pk).exists())

    def test_timeslot_deletion(self):
        availability = UserAvailability.objects.create(user=self.user, timeslot=self.timeslot)
        self.timeslot.delete()
        self.assertFalse(UserAvailability.objects.filter(pk=availability.pk).exists())

class UserSignalsTest(TestCase):
    def test_add_lecturer_role_on_user_create(self):
        pass
    
    def test_add_demonstrator_role_on_user_save(self):
        pass
    
    def test_add_lecturer_role_on_user_create(self):
        pass
    
    def test_add_demonstrator_role_on_user_save(self):
        pass