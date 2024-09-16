from django.core.management.base import BaseCommand, CommandParser
from users.models import User

class Command(BaseCommand):
    """The `Command` class defines a custom Django management command to delete all users marked as fake. 
    This command is useful for cleaning up test data from the database.

    :param help: A brief description of what the command does, which is displayed when the `help` flag is used.
    :type help: str
    """
    help = "Delete all users marked as fake"
    
    def handle(self, *args, **kwargs):
        """Handle the execution of the command. This method retrieves and deletes all users 
        that have the `is_fake` flag set to `True`. It also provides feedback on the number of users deleted.

        :param args: Additional positional arguments.
        :type args: list
        :param kwargs: A dictionary of options passed to the command.
        :type kwargs: dict
        :return: A success message indicating the number of fake users deleted.
        :rtype: str or None
        """
        fake_users = User.objects.filter(is_fake=True)
        count = fake_users.count()
        fake_users.delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} fake users.'))