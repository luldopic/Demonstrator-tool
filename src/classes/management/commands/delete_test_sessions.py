from django.core.management.base import BaseCommand
from classes.models import ModuleSession


class Command(BaseCommand):
    """The `Command` class defines a custom Django management command to delete all module sessions that are marked 
    as test sessions. This command is useful for cleaning up test data from the database.

    :param help: A brief description of what the command does, which is displayed when the `help` flag is used.
    :type help: str
    """
    help = "Delete all module sessions marked as test"
    
    
    def handle(self, *args, **options) -> str | None:
        """Handle the execution of the command, which deletes all module sessions where the `test_session` flag is `True`. 
        The method also provides feedback on the number of sessions deleted.

        :param args: Additional positional arguments.
        :type args: list
        :param options: A dictionary of options passed to the command.
        :type options: dict
        :return: A success message indicating the number of test sessions deleted.
        :rtype: str or None
        """
        test_sessions = ModuleSession.objects.filter(test_session=True)
        count = test_sessions.count()
        test_sessions.delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} test sessions'))