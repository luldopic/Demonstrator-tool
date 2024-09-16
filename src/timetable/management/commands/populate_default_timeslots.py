from django.core.management.base import BaseCommand, CommandError
from timetable.models import Timeslot
from timetable.utils import Timetable

from datetime import datetime


class Command(BaseCommand):
    """The `Command` class defines a custom Django management command to populate the database with default timeslots.
    This command reads timeslot data from a predefined timetable and saves them into the `Timeslot` model.

    :param help: A brief description of what the command does, which is displayed when the `help` flag is used.
    :type help: str
    """
    help = "Populates Timeslots with default timeslots"
    
    WEEKDAY_MAP = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6
    }
        
    def handle(self, *args, **options):
        """Handle the execution of the command. This method initializes a timetable, iterates through its timeslots, 
        and saves them into the database. It raises errors if the timetable generation fails or if an invalid day is encountered.

        :param args: Additional positional arguments.
        :type args: list
        :param options: A dictionary of options passed to the command.
        :type options: dict
        :return: A success message upon completion or raises a `CommandError`.
        :rtype: str or None
        """    
        try: 
            timetable = Timetable()
        except Exception as e:
            raise CommandError(f"Error generating timetable: {e}")
                
        for slot in timetable.timeslot:
            day_integer = self.WEEKDAY_MAP.get(slot[0], None)
            if day_integer is None:
                raise CommandError(f"Invalid day: {slot[0]}")
            start_time_object = datetime.strptime(slot[1],"%H:%M").time()
            end_time_object = datetime.strptime(slot[2],"%H:%M").time()
            timeslot = Timeslot(day = day_integer,
                                start_time = start_time_object,
                                end_time = end_time_object)
            timeslot.save()
        
        self.stdout.write(self.style.SUCCESS("Successfully populated default timeslots"))
            