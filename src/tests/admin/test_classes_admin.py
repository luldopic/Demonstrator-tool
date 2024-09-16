from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from classes.models import Module, ModuleSession, Skill, RequirementSkill, SessionSchedule, Competency
from timetable.models import Timeslot, Semester
from users.models import User, Lecturer, Demonstrator
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from unittest.mock import Mock
from classes.admin import (
    SkillAdmin, ModuleAdmin, ModuleSessionAdmin, RequirementsAdmin,
    CompetencyAdmin, SessionScheduleAdmin
)
from django.urls import reverse

class SkillAdminTest(TestCase):
    """The `SkillAdminTest` class contains test cases for the `SkillAdmin` class in the Django admin interface.

    :param setUp: Initializes the test environment, including creating instances of `SkillAdmin` and `Skill`.
    :type setUp: Method
    :param test_search_fields: Tests that the search fields for the `SkillAdmin` class are correctly configured.
    :type test_search_fields: Method
    :param test_save_model: Tests the `save_model` method to ensure that saving a new skill correctly creates entries for all skill levels.
    :type test_save_model: Method
    """
    def setUp(self):
        self.site = AdminSite()
        self.skill_admin = SkillAdmin(Skill, self.site)
        self.skill = Skill.objects.create(name="Programming")

    def test_search_fields(self):
        self.assertEqual(self.skill_admin.search_fields, ["name"])

    def test_save_model(self):
        request = self._mock_request()
        new_skill = Skill(name='Python')
        self.skill_admin.save_model(request, new_skill, None, change=False)
        
        skills = Skill.objects.filter(name='Python')
        self.assertEqual(skills.count(), len(Skill.LEVEL_CHOICES))
        self.assertTrue(skills.filter(level=0).exists())
        self.assertTrue(skills.filter(level=1).exists())
        self.assertTrue(skills.filter(level=2).exists())

    def _mock_request(self):
        request = RequestFactory().get('/admin/')

        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        request.session.save()

        messages_middleware = MessageMiddleware(Mock())
        messages_middleware.process_request(request)
        setattr(request, '_messages', FallbackStorage(request))

        return request


class ModuleAdminTest(TestCase):
    """The `ModuleAdminTest` class contains test cases for the `ModuleAdmin` class in the Django admin interface.

    :param setUp: Initializes the test environment, including creating instances of `ModuleAdmin`, `Lecturer`, `Semester`, and `Module`.
    :type setUp: Method
    :param test_list_display: Tests that the list display fields for the `ModuleAdmin` class are correctly configured.
    :type test_list_display: Method
    :param test_view_module_sessions: Tests the `view_module_sessions` method to ensure it returns the correct URL for viewing module sessions.
    :type test_view_module_sessions: Method
    :param test_num_sessions: Tests the `num_sessions` method to ensure it returns the correct number of session types.
    :type test_num_sessions: Method
    :param test_num_schedules: Tests the `num_schedules` method to ensure it returns the correct number of timeslots.
    :type test_num_schedules: Method
    """
    def setUp(self):
        self.site = AdminSite()
        self.module_admin = ModuleAdmin(Module, self.site)
        self.lecturer_user = User.objects.create(username="lecturer", first_name="John", last_name="Doe", email = "test@test.com")
        self.lecturer = Lecturer.objects.create(user=self.lecturer_user)
        self.semester = Semester.objects.create(year="2023/2024", semester=0)
        self.module = Module.objects.create(class_code="CS101", name="Intro to CS", lecturer=self.lecturer, semester=self.semester)

    def test_list_display(self):
        self.assertEqual(
            self.module_admin.list_display,
            ["class_code", 'name', "formatted_lecturer_name", "formatted_semester", "num_sessions", "num_schedules", "view_module_sessions"]
        )

    def test_view_module_sessions(self):
        url = self.module_admin.view_module_sessions(self.module)
        self.assertIn(reverse("admin:classes_modulesession_changelist"), url)
        self.assertIn("CS101", url)

    def test_num_sessions(self):
        self.module.count_sessions = Mock(return_value=(2, 3))
        self.assertEqual(self.module_admin.num_sessions(self.module), 2)

    def test_num_schedules(self):
        self.module.count_sessions = Mock(return_value=(2, 3))
        self.assertEqual(self.module_admin.num_schedules(self.module), 3)

    def _mock_request(self):
        request = RequestFactory().get('/admin/')
        request.user = self.lecturer_user

        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        request.session.save()

        messages_middleware = MessageMiddleware(Mock())
        messages_middleware.process_request(request)
        setattr(request, '_messages', FallbackStorage(request))

        return request


class ModuleSessionAdminTest(TestCase):
    """The `ModuleSessionAdminTest` class contains test cases for the `ModuleSessionAdmin` class in the Django admin interface.

    :param setUp: Initializes the test environment, including creating instances of `ModuleSessionAdmin`, `Module`, `ModuleSession`, and `Timeslot`.
    :type setUp: Method
    :param test_list_display: Tests that the list display fields for the `ModuleSessionAdmin` class are correctly configured.
    :type test_list_display: Method
    :param test_total_required_demonstrators: Tests the `total_required_demonstrators` method to ensure it correctly calculates the total required demonstrators.
    :type test_total_required_demonstrators: Method
    :param test_ensure_correct_allocation: Tests the `ensure_correct_allocation` method to ensure it correctly adjusts the allocation for the selected module sessions.
    :type test_ensure_correct_allocation: Method
    """
    def setUp(self):
        self.site = AdminSite()
        self.module_session_admin = ModuleSessionAdmin(ModuleSession, self.site)
        self.lecturer_user = User.objects.create(username="lecturer", first_name="John", last_name="Doe", email = "test@test.com")
        self.lecturer = Lecturer.objects.create(user=self.lecturer_user)
        self.semester = Semester.objects.create(year="2023/2024", semester=0)
        self.module = Module.objects.create(class_code="CS101", name="Intro to CS", lecturer=self.lecturer, semester=self.semester)
        self.module_session = ModuleSession.objects.create(class_code=self.module, session_type="Lab", required_demonstrator=2)
        self.timeslot = Timeslot.objects.create(day=0, start_time="08:00:00", end_time="09:00:00")

    def test_list_display(self):
        self.assertEqual(
            self.module_session_admin.list_display,
            ["get_class_code", "session_type", "required_demonstrator", "view_module"]
        )

    def test_total_required_demonstrators(self):
        request = self._mock_request()
        queryset = ModuleSession.objects.filter(id=self.module_session.id)
        self.module_session_admin.total_required_demonstrators(request, queryset)
        messages = [str(msg) for msg in request._messages]
        self.assertIn("Total required demonstrator: 2", messages)

    def test_ensure_correct_allocation(self):
        request = self._mock_request()
        queryset = ModuleSession.objects.filter(id=self.module_session.id)
        self.module_session_admin.ensure_correct_allocation(request, queryset)

    def _mock_request(self):
        request = RequestFactory().get('/admin/')
        request.user = self.lecturer_user

        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        request.session.save()

        messages_middleware = MessageMiddleware(Mock())
        messages_middleware.process_request(request)
        setattr(request, '_messages', FallbackStorage(request))

        return request


class RequirementsAdminTest(TestCase):
    """The `RequirementsAdminTest` class contains test cases for the `RequirementsAdmin` class in the Django admin interface.

    :param setUp: Initializes the test environment, including creating instances of `RequirementsAdmin`, `Module`, `ModuleSession`, `Skill`, and `RequirementSkill`.
    :type setUp: Method
    :param test_list_display: Tests that the list display fields for the `RequirementsAdmin` class are correctly configured.
    :type test_list_display: Method
    :param test_search_fields: Tests that the search fields for the `RequirementsAdmin` class are correctly configured.
    :type test_search_fields: Method
    """
    def setUp(self):
        self.site = AdminSite()
        self.requirements_admin = RequirementsAdmin(RequirementSkill, self.site)
        self.lecturer_user = User.objects.create(username="lecturer", first_name="John", last_name="Doe", email = "test@test.com")
        self.lecturer = Lecturer.objects.create(user=self.lecturer_user)
        self.semester = Semester.objects.create(year="2023/2024", semester=0)
        self.module = Module.objects.create(class_code="CS101", name="Intro to CS", lecturer=self.lecturer, semester=self.semester)
        self.module_session = ModuleSession.objects.create(class_code=self.module, session_type="Lab", required_demonstrator=2)
        Skill.objects.create(name="Programming")
        self.skill = Skill.objects.get(name = "Programming", level = 1)
        self.requirement = RequirementSkill.objects.create(class_session=self.module_session, skill=self.skill)

    def test_list_display(self):
        self.assertEqual(self.requirements_admin.list_display, ["get_class_code", "get_skill_display"])

    def test_search_fields(self):
        self.assertEqual(self.requirements_admin.search_fields, ["class_session__class_code__class_code", "skill__name"])

class CompetencyAdminTest(TestCase):
    """The `CompetencyAdminTest` class contains test cases for the `CompetencyAdmin` class in the Django admin interface.

    :param setUp: Initializes the test environment, including creating instances of `CompetencyAdmin`, `User`, `Demonstrator`, `Skill`, and `Competency`.
    :type setUp: Method
    :param test_list_display: Tests that the list display fields for the `CompetencyAdmin` class are correctly configured.
    :type test_list_display: Method
    :param test_search_fields: Tests that the search fields for the `CompetencyAdmin` class are correctly configured.
    :type test_search_fields: Method
    """
    def setUp(self):
        self.site = AdminSite()
        self.competency_admin = CompetencyAdmin(Competency, self.site)
        self.user = User.objects.create(username="demonstrator", first_name="Demo", last_name="User", email = "test@test.com", is_demonstrator = True)
        self.demonstrator = Demonstrator.objects.get(user = self.user)
        Skill.objects.create(name="Programming")
        self.skill = Skill.objects.get(name = "Programming", level = 1)
        self.competency = Competency.objects.create(demonstrator=self.demonstrator, skill=self.skill)

    def test_list_display(self):
        self.assertEqual(self.competency_admin.list_display, ["get_demonstrator_name", "get_skill_display"])

    def test_search_fields(self):
        self.assertEqual(self.competency_admin.search_fields, ["skill__name"])

class SessionScheduleAdminTest(TestCase):
    """The `SessionScheduleAdminTest` class contains test cases for the `SessionScheduleAdmin` class in the Django admin interface.

    :param setUp: Initializes the test environment, including creating instances of `SessionScheduleAdmin`, `Module`, `ModuleSession`, `Timeslot`, and `SessionSchedule`.
    :type setUp: Method
    :param test_list_display: Tests that the list display fields for the `SessionScheduleAdmin` class are correctly configured.
    :type test_list_display: Method
    :param test_search_fields: Tests that the search fields for the `SessionScheduleAdmin` class are correctly configured.
    :type test_search_fields: Method
    """
    def setUp(self):
        self.site = AdminSite()
        self.session_schedule_admin = SessionScheduleAdmin(SessionSchedule, self.site)
        self.lecturer_user = User.objects.create(username="lecturer", first_name="John", last_name="Doe", email = "test@test.com")
        self.lecturer = Lecturer.objects.create(user=self.lecturer_user)
        self.semester = Semester.objects.create(year="2023/2024", semester=0)
        self.module = Module.objects.create(class_code="CS101", name="Intro to CS", lecturer=self.lecturer, semester=self.semester)
        self.module_session = ModuleSession.objects.create(class_code=self.module, session_type="Lab", required_demonstrator=2)
        self.timeslot = Timeslot.objects.create(day=0, start_time="08:00:00", end_time="09:00:00")
        self.session_schedule = SessionSchedule.objects.create(class_session=self.module_session, timeslot=self.timeslot)

    def test_list_display(self):
        self.assertEqual(self.session_schedule_admin.list_display, ["get_class_code", "get_class_type", "timeslot"])

    def test_search_fields(self):
        self.assertEqual(self.session_schedule_admin.search_fields, ["class_session__class_code__class_code"])
