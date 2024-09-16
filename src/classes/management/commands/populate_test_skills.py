from django.core.management.base import BaseCommand, CommandParser
from classes.models import Skill, SkillManager
import csv, os


class Command(BaseCommand):
    """The `Command` class defines a custom Django management command to populate the database with a list of skills 
    from a CSV file. This command is useful for bulk importing skill data into the database.

    :param help: A brief description of what the command does, which is displayed when the `help` flag is used.
    :type help: str
    """
    help = "Populates database with list of skills from csv"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Define the arguments that the command accepts. The command requires a CSV file to read the skill data from.

        :param parser: The argument parser for the command.
        :type parser: CommandParser
        """
        parser.add_argument("csv_file", type=str, help="The CSV File to read data from")#
        
    def handle(self, *args, **options) -> str | None:
        """Handle the execution of the command. This method reads skill data from the provided CSV file 
        and creates new skill records in the database.

        :param args: Additional positional arguments.
        :type args: list
        :param options: A dictionary of options passed to the command, including the CSV file path.
        :type options: dict
        :return: A success or error message indicating the operation performed.
        :rtype: str or None
        """
        csv_file = options["csv_file"]
        
        self.stdout.write(f"Current working directory: {os.getcwd()}")
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file}"))
            return
        
        with open(csv_file, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row["Skill Name"]
                
                Skill.objects.create(name = name)