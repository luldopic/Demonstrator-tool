from django.test import TestCase
from django.core.management import call_command
from unittest.mock import patch, MagicMock
from timetable.models import Timeslot, Semester
from datetime import datetime


class PopulateDefaultTimeslotsTest(TestCase):
    def setUp(self):
        Timeslot.objects.all().delete()

    @patch('timetable.utils.Timetable')
    def test_populate_default_timeslots(self, MockTimetable):
        mock_timeslots = [
            ('Monday', '09:00', '10:00'),
            ('Tuesday', '10:00', '11:00'),
        ]
        MockTimetable.return_value.timeslot = mock_timeslots


        call_command('populate_default_timeslots')

        self.assertEqual(Timeslot.objects.count(), len(mock_timeslots))
        
        for day, start_str, end_str in mock_timeslots:
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()
            timeslot = Timeslot.objects.get(day=self._day_to_integer(day), start_time=start_time, end_time=end_time)
            self.assertIsNotNone(timeslot)

    def _day_to_integer(self, day):
        weekday_map = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6
        }
        return weekday_map[day]
    
class CreateSemesterCommandTest(TestCase):
    def setUp(self):
        Semester.objects.all().delete()
        
    def test_create_new_correctly(self):
        pass
        