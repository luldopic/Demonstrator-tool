from django.core.management.base import BaseCommand, CommandParser
from classes.models import Module
from users.models import Lecturer
from timetable.models import Semester
import csv


class Command(BaseCommand):
    """The `Command` class defines a custom Django management command to populate the database with a list of modules 
    from a CSV file. This command is useful for bulk importing or updating module data in the database.

    :param help: A brief description of what the command does, which is displayed when the `help` flag is used.
    :type help: str
    """

    help = "Populates database with list of modules from csv"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Define the arguments that the command accepts. The command requires a CSV file to read the module data from.

        :param parser: The argument parser for the command.
        :type parser: CommandParser
        """
        parser.add_argument("csv_file", type=str, help="The CSV File to read data from")#
        
    def handle(self, *args, **options) -> str | None:
        """Handle the execution of the command. This method reads module data from the provided CSV file, 
        and either creates new module records or updates existing ones in the database.

        :param args: Additional positional arguments.
        :type args: list
        :param options: A dictionary of options passed to the command, including the CSV file path.
        :type options: dict
        :return: A success message indicating the operation performed for each module.
        :rtype: str or None
        """
        csv_file = options["csv_file"]
        
        with open(csv_file, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                class_code = row["Module code"]
                name = row["Module name"]
                semester_info = row["Semester"]
                
                semester_name = 2              
                if "Semester 1" in semester_info:
                    semester_name = 0
                elif "Semester 2" in semester_info:
                    semester_name = 1
                    
                semester, _  = Semester.objects.get_or_create(
                    year = semester_info.split(" ")[-1],
                    semester = semester_name                    
                )
                
                module, created = Module.objects.update_or_create(
                    class_code = class_code,
                    defaults= {
                        "name" : name,
                        "semester": semester
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created module {class_code}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated module {class_code}'))