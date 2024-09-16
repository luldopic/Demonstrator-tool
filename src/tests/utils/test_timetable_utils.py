from django.test import TestCase
from timetable.utils import Timetable

class TimetableUtilTests(TestCase):
    """The `TimetableUtilTests` class contains test cases for the `Timetable` utility class in the Django application.

    :param setUp: Initializes the test environment, including creating an instance of `Timetable`.
    :type setUp: Method
    :param test_initialisation: Tests the initialization of the `Timetable` class to ensure it creates the correct number of timeslots.
    :type test_initialisation: Method
    :param test_generate_timeslots: Tests the `generate_time_slots` method to ensure it generates a valid set of timeslots.
    :type test_generate_timeslots: Method
    :param test_populate_timetable: Tests the `populate_timeslot` method to ensure it populates the timetable with valid data.
    :type test_populate_timetable: Method
    """
    def setUp(self):
        self.test_timetable = Timetable()
    
    def test_initialisation(self):
        self.assertIsInstance(self.test_timetable.timeslot, list)
        self.assertEqual(len(self.test_timetable.timeslot), 63)
    
    def test_generate_timeslots(self):
        timeslot = Timetable.generate_time_slots()
        self.assertTrue(("09:00","10:00") in timeslot)
        self.assertTrue(("17:00","18:00") in timeslot)
        
    def test_populate_timetable(self):
        timetable = []
        Timetable.populate_timeslot(timetable)
        self.assertTrue(("Monday","09:00","10:00") in timetable)
