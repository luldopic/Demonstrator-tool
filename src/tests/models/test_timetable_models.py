import tests
from django.test import TestCase
from unittest.mock import patch, MagicMock
from timetable.models import Timeslot, Semester
from datetime import time, date
import random
from django.db.utils import IntegrityError


class TimeslotModelTest(TestCase):
    """The `TimeslotModelTest` class contains test cases for the `Timeslot` model in the Django application.

    :param setUp: Initializes the test environment, creating an instance of `Timeslot`.
    :type setUp: Method
    :param test_timeslot_creation: Tests the creation of a `Timeslot` instance and verifies that it is saved correctly.
    :type test_timeslot_creation: Method
    :param test_timeslot_day_choices: Tests that the day choices for `Timeslot` are correctly configured.
    :type test_timeslot_day_choices: Method
    :param test_get_random_slot: Tests the `get_random_slot` method to ensure it returns a random timeslot or `None` if no timeslots exist.
    :type test_get_random_slot: Method
    :param test_are_same_day: Tests the `are_same_day` method to ensure it correctly identifies if all timeslots are on the same day.
    :type test_are_same_day: Method
    :param test_get_next: Tests the `get_next` method to ensure it returns the correct next timeslot.
    :type test_get_next: Method
    :param test_unique_together: Tests the unique constraint on the `day`, `start_time`, and `end_time` fields to ensure duplicate timeslots cannot be created.
    :type test_unique_together: Method
    """
    def setUp(self):
        self.timeslot = Timeslot.objects.create(
            day=0,
            start_time=time(9, 0),
            end_time=time(10, 0)
        )

    def test_timeslot_creation(self):
        self.assertTrue(isinstance(self.timeslot, Timeslot))
        day_name = dict(self.timeslot.WEEKDAY)[self.timeslot.day]
        start_time_formatted = self.timeslot.start_time.strftime("%H:%M")
        end_time_formatted = self.timeslot.end_time.strftime("%H:%M")
        self.assertEqual(self.timeslot.__str__(), f'Timeslot({day_name}, {start_time_formatted}, {end_time_formatted})')

    def test_timeslot_day_choices(self):
        choices = [choice[0] for choice in Timeslot.WEEKDAY]
        self.assertIn(self.timeslot.day, choices)
        
    def test_get_random_slot(self):
        Timeslot.objects.all().delete()
        self.assertEqual(Timeslot.get_random_slot(), None)
        
        self.timeslot1 = Timeslot.objects.create(
            day=0,
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        self.assertEqual(Timeslot.get_random_slot(),self.timeslot1)
        
        self.timeslot2 = Timeslot.objects.create(
            day=0,
            start_time=time(11, 0),
            end_time=time(12, 0)
        )
        random.seed(1)
        self.assertEqual(Timeslot.get_random_slot(),self.timeslot1)
        random.seed(5)
        self.assertEqual(Timeslot.get_random_slot(),self.timeslot2)
        
    def test_are_same_day(self):
        self.timeslot1 = Timeslot.objects.create(
            day=0,
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        
        self.timeslot2 = Timeslot.objects.create(
            day=1,
            start_time=time(11, 0),
            end_time=time(12, 0)
        )
        test1 = [self.timeslot] #True
        test2 = [self.timeslot, self.timeslot1] #True
        test3 = [self.timeslot, self.timeslot2] #False
        test4 = [self.timeslot, self.timeslot1, self.timeslot2] #False
        self.assertTrue(Timeslot.are_same_day(test1))
        self.assertTrue(Timeslot.are_same_day(test2))
        self.assertFalse(Timeslot.are_same_day(test3))
        self.assertFalse(Timeslot.are_same_day(test4))
    
    def test_get_next(self):
        Timeslot.objects.all().delete()
        self.assertEqual(self.timeslot.get_next(), None)
        
        self.timeslot1 = Timeslot.objects.create(
            day=0,
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        self.assertEqual(self.timeslot1.get_next(),self.timeslot1)
        
        self.timeslot2 = Timeslot.objects.create(
            day=0,
            start_time=time(11, 0),
            end_time=time(12, 0)
        )
        
        self.assertEqual(self.timeslot1.get_next(),self.timeslot2)
        self.assertEqual(self.timeslot2.get_next(),self.timeslot1)
        
    def test_unique_together(self):
        with self.assertRaises(IntegrityError):
            Timeslot.objects.create(
                day=self.timeslot.day,
                start_time=self.timeslot.start_time,
                end_time=self.timeslot.end_time
            )
            
class SemesterModelTest(TestCase):
    """The `SemesterModelTest` class contains test cases for the `Semester` model in the Django application.

    :param setUp: Initializes the test environment, creating an instance of `Semester`.
    :type setUp: Method
    :param test_semester_creation: Tests the creation of a `Semester` instance and verifies that it is saved correctly.
    :type test_semester_creation: Method
    :param test_semester_date_validation: Tests that the start date is before the end date for a `Semester`.
    :type test_semester_date_validation: Method
    :param test_unique_together: Tests the unique constraint on the `year` and `semester` fields to ensure duplicate semesters cannot be created.
    :type test_unique_together: Method
    """
    def setUp(self):
        self.semester = Semester.objects.create(
            year=2023,
            semester=0,
            start_date=date(2023, 9, 1),
            end_date=date(2023, 12, 15)
        )

    def test_semester_creation(self):
        self.assertTrue(isinstance(self.semester, Semester))
        semester_name = dict(self.semester.SEMESTER_NAME)[self.semester.semester]
        self.assertEqual(self.semester.__str__(), 
                         f'Semester({self.semester.year}, {semester_name}, {self.semester.start_date}, {self.semester.end_date})')

    def test_semester_date_validation(self):
        self.assertLess(self.semester.start_date, self.semester.end_date)
        
    def test_unique_together(self):
        with self.assertRaises(IntegrityError):
            Semester.objects.create(
                year=self.semester.year,
                semester=self.semester.semester,
                start_date=date(2023, 9, 1),
                end_date=date(2023, 12, 15)
            )
