from datetime import datetime, timedelta

class Timetable:
    """The `Timetable` class represents a weekly schedule. It provides functionality to generate time slots, 
    populate them into a schedule, and manage the timetable for an entire week.

    :param timeslot: A list that stores all time slots generated for the week.
    :type timeslot: list
    """
    def __init__(self) -> None:
        """Initialize the `Timetable` by generating and populating time slots for the week."""
        self.timeslot: list = []
        Timetable.populate_timeslot(self.timeslot)
    
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
        """Populate the timetable with time slots for each day of the week. Each slot is stored as a tuple.

        :param timetable: The list to populate with time slots.
        :type timetable: list
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
                timetable.append(tuple(temp_slot))