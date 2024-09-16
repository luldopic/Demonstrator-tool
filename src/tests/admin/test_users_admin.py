from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.messages import get_messages
from django.contrib.sessions.middleware import SessionMiddleware
from users.models import User, Lecturer, Demonstrator
from classes.models import UserAvailability
from timetable.models import Timeslot
from users.admin import UserAdmin, LecturerAdmin, DemonstratorAdmin
from classes.admin_inlines import skill_inline, module_lecturer_inline
from unittest.mock import Mock
from django.urls import reverse

class UserAdminTest(TestCase):
    """The `UserAdminTest` class contains test cases for the `UserAdmin` class in the Django admin interface.

    :param setUp: Initializes the test environment, including creating instances of `UserAdmin`, `User`, and `Timeslot`.
    :type setUp: Method
    :param _mock_request: Mocks a request for testing purposes, including session and message middleware.
    :type _mock_request: Method
    :param test_search_fields: Tests that the search fields for the `UserAdmin` class are correctly configured.
    :type test_search_fields: Method
    :param test_list_display: Tests that the list display fields for the `UserAdmin` class are correctly configured.
    :type test_list_display: Method
    :param test_create_user_availability: Tests the `create_user_availability` method to ensure it correctly creates or updates user availability records.
    :type test_create_user_availability: Method
    """
    def setUp(self):
        self.site = AdminSite()
        self.factory = RequestFactory()
        self.user_admin = UserAdmin(User, self.site)
        self.user = User.objects.create(username="testuser", first_name="Test", last_name="User")
        self.timeslot1 = Timeslot.objects.create(day=0, start_time="08:00:00", end_time="09:00:00")
        self.timeslot2 = Timeslot.objects.create(day=1, start_time="09:00:00", end_time="10:00:00")
    
    def _mock_request(self):
        request = self.factory.get('/admin/')
        request.user = self.user

        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        request.session.save()

        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        return request

    def test_search_fields(self):
        self.assertEqual(self.user_admin.search_fields, ["first_name", "last_name", "username"])

    def test_list_display(self):
        self.assertEqual(self.user_admin.list_display, ["username", "first_name", "last_name"])

    def test_create_user_availability(self):
        queryset = User.objects.filter(id=self.user.id)
        request = self._mock_request()
        self.user_admin.create_user_availability(request, queryset)

        self.assertTrue(UserAvailability.objects.filter(user=self.user, timeslot=self.timeslot1).exists())
        self.assertTrue(UserAvailability.objects.filter(user=self.user, timeslot=self.timeslot2).exists())

        storage = get_messages(request)
        messages = [str(message) for message in storage]
        self.assertIn('User availability created/updated for 1 users.', messages)

class LecturerAdminTest(TestCase):
    """The `LecturerAdminTest` class contains test cases for the `LecturerAdmin` class in the Django admin interface.

    :param setUp: Initializes the test environment, including creating instances of `LecturerAdmin`, `User`, and `Lecturer`.
    :type setUp: Method
    :param test_inlines: Tests that the correct inline models are included in the `LecturerAdmin` class.
    :type test_inlines: Method
    :param test_search_fields: Tests that the search fields for the `LecturerAdmin` class are correctly configured.
    :type test_search_fields: Method
    :param test_list_display: Tests that the list display fields for the `LecturerAdmin` class are correctly configured.
    :type test_list_display: Method
    """
    def setUp(self):
        self.site = AdminSite()
        self.lecturer_admin = LecturerAdmin(Lecturer, self.site)
        self.user = User.objects.create(username="lectureruser", first_name="Lecturer", last_name="User")
        self.lecturer = Lecturer.objects.create(user=self.user, department="Science")

    def test_inlines(self):
        self.assertIn(module_lecturer_inline.ModuleInline, self.lecturer_admin.inlines)

    def test_search_fields(self):
        self.assertEqual(self.lecturer_admin.search_fields, ["get_first_name", "get_last_name", "department"])

    def test_list_display(self):
        self.assertEqual(self.lecturer_admin.list_display, ["get_first_name", "get_last_name", "department", "view_user"])

class DemonstratorAdminTest(TestCase):
    """The `DemonstratorAdminTest` class contains test cases for the `DemonstratorAdmin` class in the Django admin interface.

    :param setUp: Initializes the test environment, including creating instances of `DemonstratorAdmin`, `User`, and `Demonstrator`.
    :type setUp: Method
    :param test_inlines: Tests that the correct inline models are included in the `DemonstratorAdmin` class.
    :type test_inlines: Method
    :param test_search_fields: Tests that the search fields for the `DemonstratorAdmin` class are correctly configured.
    :type test_search_fields: Method
    :param test_list_display: Tests that the list display fields for the `DemonstratorAdmin` class are correctly configured.
    :type test_list_display: Method
    """
    def setUp(self):
        self.site = AdminSite()
        self.demonstrator_admin = DemonstratorAdmin(Demonstrator, self.site)
        self.user = User.objects.create(username="demonstratoruser", first_name="Demonstrator", last_name="User")
        self.demonstrator = Demonstrator.objects.create(user=self.user)

    def test_inlines(self):
        self.assertIn(skill_inline.CompetencyInline, self.demonstrator_admin.inlines)

    def test_search_fields(self):
        self.assertEqual(self.demonstrator_admin.search_fields, ["get_first_name", "get_last_name", "competency__skill__name"])

    def test_list_display(self):
        self.assertEqual(self.demonstrator_admin.list_display, ["get_first_name", "get_last_name", "view_user"])