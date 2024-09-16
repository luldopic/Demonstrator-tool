from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from classes.models import Skill

class Command(BaseCommand):
    """The `Command` class defines a custom Django management command to add a new skill to the `Skill` database. 
    This command accepts the name of the skill as an argument and creates a new skill entry in the database.

    :param help: A brief description of what the command does, which is displayed when the `help` flag is used.
    :type help: str
    """
    help = "Add a new skill in skill database"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Define the arguments that the command accepts. In this case, the command requires a single argument, 
        the name of the skill.

        :param parser: The argument parser for the command.
        :type parser: CommandParser
        """
        parser.add_argument("name", type=str, help="Name of skill")
        
    def handle(self, *args: Any, **options: Any) -> str | None:
        """Handle the logic for creating a new skill in the database. This method is executed when the command is run. 
        It retrieves the skill name from the options, creates a new `Skill` instance, and provides feedback to the user.

        :param args: Additional positional arguments.
        :type args: list
        :param options: A dictionary of options passed to the command.
        :type options: dict
        :return: A success message if the skill is created successfully, or `None`.
        :rtype: str or None
        """
        name = options["name"]
        skills = Skill.objects.create(name=name)
        
        for skill in skills:
            self.stdout.write(self.style.SUCCESS(f'Skill {skill.name} at level {skill.get_level_display()} created successfully'))