from django.core.management.base import BaseCommand, CommandParser
from users.models import User, UserAvailability
from timetable.models import Timeslot
from faker import Faker
import random

class Command(BaseCommand):
    """The `Command` class defines a custom Django management command to generate random users for testing purposes. 
    This command can create either general test users or test demonstrators, with options to specify the number of users.

    :param help: A brief description of what the command does, which is displayed when the `help` flag is used.
    :type help: str
    """
    help = "Generates random users for testing purposes"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Define the arguments that the command accepts. The command allows the user to specify the total number 
        of test users to create or the number of test demonstrators to create.

        :param parser: The argument parser for the command.
        :type parser: CommandParser
        """
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--total", type=int, help="Indicates the number of test users to add")
        group.add_argument("--demonstrator", type=int, help="Indicates the number of test demonstrators to add")
        
    def handle(self, *args, **kwargs):
        """Handle the execution of the command. This method generates random user data using the `Faker` library, 
        ensures unique usernames and emails, and creates `User` objects in the database. If the `--demonstrator` flag 
        is provided, it ensures that all created users are demonstrators.

        :param args: Additional positional arguments.
        :type args: list
        :param kwargs: A dictionary of options passed to the command, including the number of users or demonstrators.
        :type kwargs: dict
        :return: None
        """
        total = kwargs.get("total", None)
        demonstrator = kwargs.get("demonstrator", None)
        if total == None:
            total = demonstrator
        faker = Faker()
        timeslots = Timeslot.objects.all()
        
        for _ in range(total):
            first_name = faker.first_name()
            last_name = faker.last_name()
            email = faker.email()
            if demonstrator == None:
                is_lecturer = random.choice([True, False])
                is_demonstrator = random.choice([True, False])
            else:
                is_lecturer = False
                is_demonstrator = True
            
            username = faker.user_name()
            while User.objects.filter(username=username).exists():
                username = faker.user_name()
            
            email = faker.email()
            while User.objects.filter(email=email).exists():
                email = faker.email()
            
            user = User.objects.create(
                username = username,
                email = email,
                first_name = first_name,
                last_name = last_name,
                is_lecturer = is_lecturer,
                is_demonstrator = is_demonstrator,
                is_fake = True
            )
            
            user.set_password(faker.password())
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'User {username} created successfully'))
        