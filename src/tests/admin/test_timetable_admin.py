from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from timetable.models import Timeslot, Semester
from classes.models import UserAvailability
from users.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from unittest.mock import Mock
from django.db.models import Q
from timetable.admin import SemesterAdmin, TimeslotAdmin, UserAvailabilityAdmin

class SemesterAdminTest(TestCase):
    """The `SemesterAdminTest` class contains test cases for the `SemesterAdmin` class in the Django admin interface.

    :param setUp: Initializes the test environment, including creating instances of `SemesterAdmin` and `Semester`.
    :type setUp: Method
    :param test_search_fields: Tests that the search fields for the `SemesterAdmin` class are correctly configured.
    :type test_search_fields: Method
    :param test_list_display: Tests that the list display fields for the `SemesterAdmin` class are correctly configured.
    :type test_list_display: Method
    """
    def setUp(self):
        self.site = AdminSite()
        self.semester_admin = SemesterAdmin(Semester, self.site)
        self.semester = Semester.objects.create(year="2023/2024", semester=0)

    def test_search_fields(self):
        self.assertEqual(self.semester_admin.search_fields, ["year", "semester"])

    def test_list_display(self):
        self.assertEqual(self.semester_admin.list_display, ["year", "semester"])

class TimeslotAdminTest(TestCase):
    """The `TimeslotAdminTest` class contains test cases for the `TimeslotAdmin` class in the Django admin interface.

    :param setUp: Initializes the test environment, including creating instances of `TimeslotAdmin` and `Timeslot`.
    :type setUp: Method
    :param test_list_display: Tests that the list display fields for the `TimeslotAdmin` class are correctly configured.
    :type test_list_display: Method
    :param test_ordering: Tests that the ordering fields for the `TimeslotAdmin` class are correctly configured.
    :type test_ordering: Method
    """
    def setUp(self):
        self.site = AdminSite()
        self.timeslot_admin = TimeslotAdmin(Timeslot, self.site)
        self.timeslot = Timeslot.objects.create(day=0, start_time="08:00:00", end_time="09:00:00")

    def test_list_display(self):
        self.assertEqual(self.timeslot_admin.list_display, ["day", "start_time", "end_time"])

    def test_ordering(self):
        self.assertEqual(self.timeslot_admin.ordering, ["day", "start_time"])

class UserAvailabilityAdminTest(TestCase):
    """The `UserAvailabilityAdminTest` class contains test cases for the `UserAvailabilityAdmin` class in the Django admin interface.

    :param setUp: Initializes the test environment, including creating instances of `UserAvailabilityAdmin`, `User`, `Timeslot`, and `UserAvailability`.
    :type setUp: Method
    :param _mock_request: Mocks a request for testing purposes, including session and message middleware.
    :type _mock_request: Method
    :param test_list_display: Tests that the list display fields for the `UserAvailabilityAdmin` class are correctly configured.
    :type test_list_display: Method
    :param test_search_fields: Tests that the search fields for the `UserAvailabilityAdmin` class are correctly configured.
    :type test_search_fields: Method
    :param test_get_search_results: Tests the custom search results method to ensure it returns the correct results based on the search term.
    :type test_get_search_results: Method
    """
    def setUp(self):
        self.site = AdminSite()
        self.user_availability_admin = UserAvailabilityAdmin(UserAvailability, self.site)
        self.factory = RequestFactory()
        self.user = User.objects.create(username="testuser", first_name="Test", last_name="User")
        self.timeslot = Timeslot.objects.create(day=0, start_time="08:00:00", end_time="09:00:00")
        self.user_availability = UserAvailability.objects.create(user=self.user, timeslot=self.timeslot, is_available=True)

    def _mock_request(self):
        request = self.factory.get('/admin/')
        request.user = self.user

        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        request.session.save()

        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        return request

    def test_list_display(self):
        self.assertEqual(self.user_availability_admin.list_display, ["get_user_name", "get_timeslot", "is_available"])

    def test_search_fields(self):
        self.assertEqual(self.user_availability_admin.search_fields, ["user__first_name", "user__last_name", "user__username"])

    def test_get_search_results(self):
        queryset = UserAvailability.objects.all()
        request = self._mock_request()
        search_term = "Test User"
        results, use_distinct = self.user_availability_admin.get_search_results(request, queryset, search_term)

        self.assertIn(self.user_availability, results)

        search_term = "Test User"
        results, use_distinct = self.user_availability_admin.get_search_results(request, queryset, search_term)
        self.assertIn(self.user_availability, results)
