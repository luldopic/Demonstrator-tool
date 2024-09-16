from django.core.management.base import BaseCommand
from users.models import User, UserAvailability
from timetable.models import Timeslot

class Command(BaseCommand):
    """The `Command` class defines a custom Django management command to generate availability records 
    for users marked as fake. This command is useful for creating test data that simulates user availability 
    across all time slots.

    :param help: A brief description of what the command does, which is displayed when the `help` flag is used.
    :type help: str
    """
    help = "Generates user availability for testing purposes"
        
    def handle(self, *args, **kwargs):
        """Handle the execution of the command. This method creates `UserAvailability` records for each fake user 
        across all available time slots, ensuring that no duplicates are created. It also provides feedback on 
        the number of users for whom availability was created.

        :param args: Additional positional arguments.
        :type args: list
        :param kwargs: A dictionary of options passed to the command.
        :type kwargs: dict
        :return: A success message indicating the number of users for whom availability was created.
        :rtype: str or None
        """
        fake_users = User.objects.filter(is_fake=True)
        timeslots = Timeslot.objects.all()
        count = 0
        for user in fake_users:
            for slot in timeslots:
                if not UserAvailability.objects.filter(user=user, timeslot=slot).exists():
                    UserAvailability.objects.create(user=user, timeslot=slot)
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'User availability created for {count} users'))