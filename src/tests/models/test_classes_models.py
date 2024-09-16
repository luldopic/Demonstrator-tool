import tests
from django.test import TestCase
from unittest.mock import patch, MagicMock
from classes.models import Module, ModuleSession, Skill, Competency, RequirementSkill, SessionSchedule
from users.models import Lecturer, User, Demonstrator, UserAvailability
from timetable.models import Semester, Timeslot
from django.db.utils import IntegrityError
from django.db.models import ProtectedError
from django.db import models


class ModuleModelTest(TestCase):
    """The `ModuleModelTest` class contains test cases for the `Module` model in the Django application.

    :param setUp: Initializes the test environment, creating instances of `Semester`, `Lecturer`, and `Module`.
    :type setUp: Method
    :param test_create_module: Tests the creation of a `Module` instance and verifies that it is saved correctly.
    :type test_create_module: Method
    :param test_formatted_lecturer_name: Tests the `formatted_lecturer_name` method to ensure it returns the correct formatted name of the lecturer.
    :type test_formatted_lecturer_name: Method
    :param test_formatted_semester: Tests the `formatted_semester` method to ensure it returns the correct formatted semester.
    :type test_formatted_semester: Method
    :param test_get_session_types: Tests the `get_session_types` method to ensure it returns the correct session types associated with the module.
    :type test_get_session_types: Method
    :param test_get_schedule: Tests the `get_schedule` method to ensure it returns the correct schedule information.
    :type test_get_schedule: Method
    :param test_has_conflict: Tests the `has_conflict` method to ensure it correctly identifies scheduling conflicts.
    :type test_has_conflict: Method
    :param test_count_sessions: Tests the `count_sessions` method to ensure it correctly counts the number of sessions and schedules.
    :type test_count_sessions: Method
    :param test_update_lecturer_availability: Tests the `update_lecturer_availability` method to ensure it updates the lecturer's availability correctly.
    :type test_update_lecturer_availability: Method
    :param test_lecturer_deletion: Tests the behavior when the associated lecturer is deleted.
    :type test_lecturer_deletion: Method
    :param test_semester_deletion: Tests the behavior when the associated semester is deleted, ensuring it raises a `ProtectedError`.
    :type test_semester_deletion: Method
    """
    def setUp(self):
        self.semester = Semester.objects.create(year="2023/2024", semester=0, start_date="2023-09-01", end_date="2024-01-15")
        self.lecturer = Lecturer.objects.create(user=User.objects.create_user(username="lecturer", password="password"))
        self.module = Module.objects.create(class_code="CS101", name="Computer Science 101", lecturer=self.lecturer, semester=self.semester)

    def test_create_module(self):
        self.assertIsNotNone(self.module.pk)
        self.assertEqual(self.module.class_code, "CS101")
        self.assertEqual(self.module.name, "Computer Science 101")
        self.assertEqual(self.module.lecturer, self.lecturer)
        self.assertEqual(self.module.semester, self.semester)

    def test_formatted_lecturer_name(self):
        formatted_name = self.module.formatted_lecturer_name()
        expected_name = f"{self.lecturer.get_first_name()} {self.lecturer.get_last_name()}"
        self.assertEqual(formatted_name, expected_name)

    def test_formatted_semester(self):
        formatted_semester = self.module.formatted_semester()
        expected_semester = "2023/2024 Semester 1"
        self.assertEqual(formatted_semester, expected_semester)

    def test_get_session_types(self):
        ModuleSession.objects.create(class_code=self.module, session_type="Lecture")
        ModuleSession.objects.create(class_code=self.module, session_type="Lab")
        session_types = self.module.get_session_types()
        self.assertEqual(session_types, (True, False, True, False))

    def test_get_schedule(self):
        session = ModuleSession.objects.create(class_code=self.module, session_type="Lecture")
        timeslot = Timeslot.objects.create(day=0, start_time="09:00", end_time="10:00")
        SessionSchedule.objects.create(class_session=session, timeslot=timeslot)
        schedule = self.module.get_schedule()
        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule[0]['session_type'], "Lecture")
        self.assertEqual(schedule[0]['timeslot'], timeslot)

    def test_has_conflict(self):
        session1 = ModuleSession.objects.create(class_code=self.module, session_type="Lecture")
        session2 = ModuleSession.objects.create(class_code=self.module, session_type="Tutorial")
        timeslot = Timeslot.objects.create(day=0, start_time="09:00", end_time="10:00")
        SessionSchedule.objects.create(class_session=session1, timeslot=timeslot)
        SessionSchedule.objects.create(class_session=session2, timeslot=timeslot)
        self.assertTrue(self.module.has_conflict())

    def test_count_sessions(self):
        session = ModuleSession.objects.create(class_code=self.module, session_type="Lecture")
        SessionSchedule.objects.create(class_session=session, timeslot=Timeslot.objects.create(day=0, start_time="09:00", end_time="10:00"))
        count_sessions, count_schedules = self.module.count_sessions()
        self.assertEqual(count_sessions, 1)
        self.assertEqual(count_schedules, 1)

    def test_update_lecturer_availability(self):
        timeslot = Timeslot.objects.create(day=0, start_time="09:00", end_time="10:00")
        session = ModuleSession.objects.create(class_code=self.module, session_type="Lecture")
        SessionSchedule.objects.create(class_session=session, timeslot=timeslot)
        self.module.update_lecturer_availability()
        availability = UserAvailability.objects.get(user=self.lecturer.user, timeslot=timeslot)
        self.assertFalse(availability.is_available)

    def test_lecturer_deletion(self):
        self.lecturer.delete()
        self.module.refresh_from_db()
        self.assertIsNone(self.module.lecturer)

    def test_semester_deletion(self):
        with self.assertRaises(models.ProtectedError):
            self.semester.delete()

class ModuleSessionModelTest(TestCase):
    """The `ModuleSessionModelTest` class contains test cases for the `ModuleSession` model in the Django application.

    :param setUp: Initializes the test environment, creating instances of `Semester`, `Lecturer`, `Module`, and `ModuleSession`.
    :type setUp: Method
    :param test_create_module_session: Tests the creation of a `ModuleSession` instance and verifies that it is saved correctly.
    :type test_create_module_session: Method
    :param test_get_class_code: Tests the `get_class_code` method to ensure it returns the correct class code.
    :type test_get_class_code: Method
    :param test_get_timeslots: Tests the `get_timeslots` method to ensure it returns the correct timeslots associated with the session.
    :type test_get_timeslots: Method
    :param test_ensure_correct_allocation: Tests the `ensure_correct_allocation` method to ensure it correctly allocates demonstrators.
    :type test_ensure_correct_allocation: Method
    :param test_custom_save: Tests the custom save method to ensure it correctly saves the `ModuleSession` and creates the necessary allocations.
    :type test_custom_save: Method
    :param test_module_deletion: Tests the behavior when the associated module is deleted, ensuring it raises a `ProtectedError`.
    :type test_module_deletion: Method
    """
    def setUp(self):
        self.semester = Semester.objects.create(year="2023/2024", semester=0, start_date="2023-09-01", end_date="2024-01-15")
        self.lecturer = Lecturer.objects.create(user=User.objects.create_user(username="lecturer", password="password"))
        self.module = Module.objects.create(class_code="CS101", name="Computer Science 101", lecturer=self.lecturer, semester=self.semester)
        self.session = ModuleSession.objects.create(class_code=self.module, session_type="Lecture", required_demonstrator=2)

    def test_create_module_session(self):
        self.assertIsNotNone(self.session.pk)
        self.assertEqual(self.session.class_code, self.module)
        self.assertEqual(self.session.session_type, "Lecture")
        self.assertEqual(self.session.required_demonstrator, 2)

    def test_get_class_code(self):
        self.assertEqual(self.session.get_class_code(), "CS101")

    def test_get_timeslots(self):
        timeslot = Timeslot.objects.create(day=0, start_time="09:00", end_time="10:00")
        SessionSchedule.objects.create(class_session=self.session, timeslot=timeslot)
        self.assertIn(timeslot, self.session.get_timeslots())

    def test_ensure_correct_allocation(self):
        self.session.ensure_correct_allocation()
        from allocations.models import Allocation
        self.assertEqual(Allocation.objects.filter(class_session=self.session).count(), 2)

    def test_custom_save(self):
        from allocations.models import Allocation
        self.session.save()
        self.assertEqual(Allocation.objects.filter(class_session=self.session).count(), 2)

    def test_module_deletion(self):
        with self.assertRaises(ProtectedError):
            self.module.delete()
            self.assertTrue(ModuleSession.objects.filter(pk=self.session.pk).exists())

class SkillManagerTest(TestCase):
    """The `SkillManagerTest` class contains test cases for the custom manager methods in the `Skill` model.

    :param test_custom_create: Tests the custom create method for the `Skill` model to ensure it creates skills with different levels.
    :type test_custom_create: Method
    :param test_value_error: Tests the behavior when trying to create a skill with an invalid name, ensuring it raises a `ValueError`.
    :type test_value_error: Method
    """
    def test_custom_create(self):
        skills = Skill.objects.create(name="Python")
        self.assertEqual(len(skills), 3)
        self.assertEqual(skills[0].name, "Python")
        self.assertEqual(skills[0].level, 0)  # Beginner
        self.assertEqual(skills[1].name, "Python")
        self.assertEqual(skills[1].level, 1)  # Intermediate
        self.assertEqual(skills[2].name, "Python")
        self.assertEqual(skills[2].level, 2)  # Expert

    def test_value_error(self):
        with self.assertRaises(ValueError):
            Skill.objects.create(name="")

class SkillModelTest(TestCase):
    """The `SkillModelTest` class contains test cases for the `Skill` model in the Django application.

    :param setUp: Initializes the test environment, creating instances of `Skill`.
    :type setUp: Method
    :param test_create_skill: Tests the creation of a `Skill` instance and verifies that it is saved correctly.
    :type test_create_skill: Method
    :param test_unique_together: Tests the unique constraint on the `name` and `level` fields to ensure duplicate skills cannot be created.
    :type test_unique_together: Method
    """
    def setUp(self):
        Skill.objects.create(name="Python")
        self.skill = Skill.objects.get(name="Python", level = 1)

    def test_create_skill(self):
        self.assertIsNotNone(self.skill.pk)
        self.assertEqual(self.skill.name, "Python")
        self.assertEqual(self.skill.level, 1)

    def test_unique_together(self):
        with self.assertRaises(IntegrityError):
            Skill.objects.create(name="Python")


class RequirementSkillModelTest(TestCase):
    """The `RequirementSkillModelTest` class contains test cases for the `RequirementSkill` model in the Django application.

    :param setUp: Initializes the test environment, creating instances of `Semester`, `Lecturer`, `Module`, `ModuleSession`, `Skill`, and `RequirementSkill`.
    :type setUp: Method
    :param test_create_requirement: Tests the creation of a `RequirementSkill` instance and verifies that it is saved correctly.
    :type test_create_requirement: Method
    :param test_unique_together: Tests the unique constraint on the `class_session` and `skill` fields to ensure duplicate requirement skills cannot be created.
    :type test_unique_together: Method
    :param test_skill_deletion: Tests the behavior when the associated skill is deleted, ensuring it raises a `ProtectedError`.
    :type test_skill_deletion: Method
    :param test_class_session_deletion: Tests the behavior when the associated class session is deleted, ensuring the requirement skill is also deleted.
    :type test_class_session_deletion: Method
    """
    def setUp(self):
        self.semester = Semester.objects.create(year="2023/2024", semester=0, start_date="2023-09-01", end_date="2024-01-15")
        self.lecturer = Lecturer.objects.create(user=User.objects.create_user(username="lecturer", password="password"))
        self.module = Module.objects.create(class_code="CS101", name="Computer Science 101", lecturer=self.lecturer, semester=self.semester)
        self.session = ModuleSession.objects.create(class_code=self.module, session_type="Lab")
        Skill.objects.create(name="Python")
        self.skill = Skill.objects.get(name="Python", level = 1)
        self.requirement_skill = RequirementSkill.objects.create(class_session=self.session, skill=self.skill)

    def test_create_requirement(self):
        self.assertIsNotNone(self.requirement_skill.pk)
        self.assertEqual(self.requirement_skill.class_session, self.session)
        self.assertEqual(self.requirement_skill.skill, self.skill)

    def test_unique_together(self):
        with self.assertRaises(IntegrityError):  # Replace Exception with IntegrityError if using Django
            RequirementSkill.objects.create(class_session=self.session, skill=self.skill)

    def test_skill_deletion(self):
        with self.assertRaises(ProtectedError):
            self.skill.delete()
            self.assertTrue(RequirementSkill.objects.filter(pk=self.requirement_skill.pk).exists())

    def test_class_session_deletion(self):
        self.session.delete()
        self.assertFalse(RequirementSkill.objects.filter(pk=self.requirement_skill.pk).exists())


class SessionScheduleModelTest(TestCase):
    """The `SessionScheduleModelTest` class contains test cases for the `SessionSchedule` model in the Django application.

    :param setUp: Initializes the test environment, creating instances of `Semester`, `Lecturer`, `Module`, `ModuleSession`, `Timeslot`, and `SessionSchedule`.
    :type setUp: Method
    :param test_create_session_schedule: Tests the creation of a `SessionSchedule` instance and verifies that it is saved correctly.
    :type test_create_session_schedule: Method
    :param test_unique_together: Tests the unique constraint on the `class_session` and `timeslot` fields to ensure duplicate schedules cannot be created.
    :type test_unique_together: Method
    :param test_class_session_deletion: Tests the behavior when the associated class session is deleted, ensuring the session schedule is also deleted.
    :type test_class_session_deletion: Method
    :param test_timeslot_deletion: Tests the behavior when the associated timeslot is deleted, ensuring it raises a `ProtectedError`.
    :type test_timeslot_deletion: Method
    """
    def setUp(self):
        self.semester = Semester.objects.create(year="2023/2024", semester=0, start_date="2023-09-01", end_date="2024-01-15")
        self.lecturer = Lecturer.objects.create(user=User.objects.create_user(username="lecturer", password="password"))
        self.module = Module.objects.create(class_code="CS101", name="Computer Science 101", lecturer=self.lecturer, semester=self.semester)
        self.session = ModuleSession.objects.create(class_code=self.module, session_type="Lecture")
        self.timeslot = Timeslot.objects.create(day=0, start_time="09:00", end_time="10:00")
        self.schedule = SessionSchedule.objects.create(class_session=self.session, timeslot=self.timeslot)

    def test_create_session_schedule(self):
        self.assertIsNotNone(self.schedule.pk)
        self.assertEqual(self.schedule.class_session, self.session)
        self.assertEqual(self.schedule.timeslot, self.timeslot)

    def test_unique_together(self):
        with self.assertRaises(IntegrityError):  # Replace Exception with IntegrityError if using Django
            SessionSchedule.objects.create(class_session=self.session, timeslot=self.timeslot)

    def test_class_session_deletion(self):
        self.session.delete()
        self.assertFalse(SessionSchedule.objects.filter(pk=self.schedule.pk).exists())

    def test_timeslot_deletion(self):
        with self.assertRaises(ProtectedError):
            self.timeslot.delete()
            self.assertTrue(SessionSchedule.objects.filter(pk=self.schedule.pk).exists())
    

class CompetencyModelTest(TestCase):
    """The `CompetencyModelTest` class contains test cases for the `Competency` model in the Django application.

    :param setUp: Initializes the test environment, creating instances of `Demonstrator`, `Skill`, and `Competency`.
    :type setUp: Method
    :param test_create_competency: Tests the creation of a `Competency` instance and verifies that it is saved correctly.
    :type test_create_competency: Method
    :param test_unique_together: Tests the unique constraint on the `skill` and `demonstrator` fields to ensure duplicate competencies cannot be created.
    :type test_unique_together: Method
    :param test_verbose_name: Tests the verbose name for the plural form of `Competency`.
    :type test_verbose_name: Method
    :param test_skill_deletion: Tests the behavior when the associated skill is deleted, ensuring the competency is also deleted.
    :type test_skill_deletion: Method
    :param test_demonstrator_deletion: Tests the behavior when the associated demonstrator is deleted, ensuring the competency is also deleted.
    :type test_demonstrator_deletion: Method
    """
    def setUp(self):
        self.demonstrator = Demonstrator.objects.create(user=User.objects.create_user(username="demo", password="password"))
        Skill.objects.create(name="Python")
        self.skill = Skill.objects.get(name="Python", level = 1)
        self.competency = Competency.objects.create(skill=self.skill, demonstrator=self.demonstrator)

    def test_create_competency(self):
        self.assertIsNotNone(self.competency.pk)
        self.assertEqual(self.competency.skill, self.skill)
        self.assertEqual(self.competency.demonstrator, self.demonstrator)

    def test_unique_together(self):
        with self.assertRaises(IntegrityError):
            Competency.objects.create(skill=self.skill, demonstrator=self.demonstrator)

    def test_verbose_name(self):
        self.assertEqual(Competency._meta.verbose_name_plural, "Competencies")

    def test_skill_deletion(self):
        self.skill.delete()
        self.assertFalse(Competency.objects.filter(pk=self.competency.pk).exists())

    def test_demonstrator_deletion(self):
        self.demonstrator.delete()
        self.assertFalse(Competency.objects.filter(pk=self.competency.pk).exists())