from django.db import models
import random
import itertools


class Timeslot(models.Model):
    """The `Timeslot` model represents a specific time slot within a week. Each time slot is associated with a day of the week, 
    and has defined start and end times.

    :param WEEKDAY: A list of tuples representing the days of the week, mapped to integers (0 for Monday, 6 for Sunday).
    :type WEEKDAY: list of tuple
    :param day: An integer field representing the day of the week.
    :type day: IntegerField
    :param start_time: The starting time for the time slot.
    :type start_time: TimeField
    :param end_time: The ending time for the time slot.
    :type end_time: TimeField
    """
    WEEKDAY = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday")
    ]
    day = models.IntegerField(choices=WEEKDAY)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        unique_together = ["day", "start_time", "end_time"]
    
    def __str__(self) -> str:
        """Return a string representation of the time slot, including the day of the week and the start and end times.

        :return: The string representation of the time slot.
        :rtype: str
        """
        day_name = dict(self.WEEKDAY)[self.day]
        start_time_formatted = self.start_time.strftime("%H:%M")
        end_time_formatted = self.end_time.strftime("%H:%M")
        return f"Timeslot({day_name}, {start_time_formatted}, {end_time_formatted})"
    
    @staticmethod
    def get_random_slot():
        """Retrieve a random time slot from the available time slots in the database.

        :return: A randomly selected `Timeslot` object, or `None` if no time slots exist.
        :rtype: Timeslot or None
        """
        timeslots = Timeslot.objects.all()
        if not timeslots.exists():
            return None
        return random.choice(timeslots)
    
    @staticmethod
    def are_same_day(timeslots):
        """Check if all the provided time slots occur on the same day.

        :param timeslots: A list of `Timeslot` objects.
        :type timeslots: list
        :return: `True` if all time slots occur on the same day, `False` otherwise.
        :rtype: bool
        """
        if not timeslots:
            return False
        first_day = timeslots[0].day
        return all(timeslot.day == first_day for timeslot in timeslots)
    
    def get_next(self):
        """Retrieve the next time slot in sequence, based on the day and start time.

        :return: The next `Timeslot` object, or `None` if no time slots exist.
        :rtype: Timeslot or None
        """
        timeslots = Timeslot.objects.all().order_by("day", "start_time")
        if not timeslots.exists():
            return None
        
        looping_timeslots = itertools.cycle(timeslots)
        for timeslot in looping_timeslots:
            if timeslot == self:
                return next(looping_timeslots)
    
    

class Semester(models.Model):
    """The `Semester` model represents an academic semester, including the year, semester name, and the start and end dates.

    :param SEMESTER_NAME: A list of tuples representing the possible semester names.
    :type SEMESTER_NAME: list of tuple
    :param year: A string representing the academic year (e.g., "2023-2024").
    :type year: CharField
    :param semester: An integer field representing the semester (0 for Semester 1, 1 for Semester 2, 2 for Full Year).
    :type semester: IntegerField
    :param start_date: The start date of the semester.
    :type start_date: DateField
    :param end_date: The end date of the semester.
    :type end_date: DateField
    """
    SEMESTER_NAME = [
        (0, "Semester 1"),
        (1, "Semester 2"),
        (2, "Full Year")
    ]
    year = models.CharField(max_length=9)
    semester = models.IntegerField(choices=SEMESTER_NAME)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    
    class Meta:
        unique_together = ["year", "semester"]
    
    def __str__(self) -> str:
        """Return a string representation of the semester, including the year, semester name, and start/end dates.

        :return: The string representation of the semester.
        :rtype: str
        """
        semester_name = dict(self.SEMESTER_NAME)[self.semester]
        return f"Semester({self.year}, {semester_name}, {self.start_date}, {self.end_date})"