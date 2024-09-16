from django.core.management.base import BaseCommand, CommandParser
from classes.models import Module

class Command(BaseCommand):
    """The `Command` class defines a custom Django management command to check if a specific module has a scheduling 
    conflict with its sessions. The command takes the module's class code as an argument and checks for conflicts.

    :param help: A brief description of what the command does, which is displayed when the `help` flag is used.
    :type help: str
    """
    help = "Checks if a module has a scheduling conflict with its sessions"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Define the arguments that the command accepts. In this case, the command requires a single argument, 
        the class code of the module to check for scheduling conflicts.

        :param parser: The argument parser for the command.
        :type parser: CommandParser
        """
        parser.add_argument('class_code', type=str, help="The code of the module you wish to check")
        
    def handle(self, *args, **kwargs):
        """Handle the logic for checking if the specified module has a scheduling conflict. This method is executed 
        when the command is run. It retrieves the module based on the provided class code, checks for conflicts, 
        and provides feedback to the user.

        :param args: Additional positional arguments.
        :type args: list
        :param kwargs: A dictionary of options passed to the command, including the class code.
        :type kwargs: dict
        :return: None
        """
        class_code = kwargs["class_code"]
        
        
        module = Module.objects.filter(class_code=class_code)
        if module.exists():
            if module.first().has_conflict():
                self.stdout.write(self.style.ERROR(f'Module with class code {class_code} has a scheduling conflict'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Module with class code {class_code} has no scheduling conflict'))
        else:
            self.stdout.write(self.style.ERROR(f'Module with class code {class_code} does not exist.'))