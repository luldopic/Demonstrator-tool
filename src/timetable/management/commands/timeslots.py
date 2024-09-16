from datetime import datetime, timedelta

class Timetable:
    """The `Timetable` class represents a weekly schedule for a given year and semester. It provides functionality 
    for generating time slots, populating them into a schedule, and identifying open (unallocated) slots.

    :param year: The academic year associated with the timetable.
    :type year: int
    :param semester: The semester associated with the timetable.
    :type semester: int
    :param timeslot: A dictionary mapping each time slot to its allocated status (None if unallocated).
    :type timeslot: dict
    """
    def __init__(self, year, semester) -> None:
        """Initialize the `Timetable` with the given year and semester, and populate the timeslot dictionary.

        :param year: The academic year.
        :type year: int
        :param semester: The semester.
        :type semester: int
        """
        self.year = year
        self.semester = semester
        self.timeslot: dict = {}
        Timetable.populate_timeslot(self.timeslot)
        
    def getOpen(self) -> list:
        """Retrieve a list of all open (unallocated) time slots.

        :return: A list of time slots that are currently unallocated.
        :rtype: list of tuple
        """
        open_slots = []
        for slot in self.timeslot.keys():
            if self.timeslot[slot] == None:
                open_slots.append(slot)
        return open_slots
    
    @staticmethod
    def generate_time_slots(start_time = "09:00", 
                            end_time = "18:00", 
                            interval_minutes = 60):
        """Generate a list of time slots for a single day, based on the given start time, end time, and interval.

        :param start_time: The starting time of the first slot (default is 09:00).
        :type start_time: str
        :param end_time: The ending time after which no slots should start (default is 18:00).
        :type end_time: str
        :param interval_minutes: The length of each time slot in minutes (default is 60 minutes).
        :type interval_minutes: int
        :return: A list of tuples, each representing a time slot (start time, end time).
        :rtype: list of tuple
        """
        start_time = datetime.strptime(start_time,"%H:%M")
        end_time = datetime.strptime(end_time, '%H:%M')
        interval = timedelta(minutes=interval_minutes)
        
        current_time = start_time
        time_slots = []
        
        while current_time <= end_time-interval:
            slot_start = current_time
            slot_end = current_time + interval
            slot = (slot_start.strftime('%H:%M'), slot_end.strftime('%H:%M'))
            time_slots.append(slot)
            current_time += interval
        
        return time_slots
    
    @staticmethod
    def populate_timeslot(timetable: dict):
        """Populate the timetable with time slots for each day of the week. Each slot is initially unallocated.

        :param timetable: The dictionary to populate with time slots.
        :type timetable: dict
        :return: None
        """
        timetable.clear()
        week = ["Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday"]
        timeslots = Timetable.generate_time_slots()
        for day in week:
            for slot in timeslots:
                temp_slot = list(slot)
                temp_slot.insert(0,day)
                timetable[tuple(temp_slot)] = None