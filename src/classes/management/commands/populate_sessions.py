from django.core.management.base import BaseCommand, CommandParser
from django.core.management import call_command
from classes.models import Module, ModuleSession, RequirementSkill, Skill
import csv, random


class Command(BaseCommand):
    """The `Command` class defines a custom Django management command to populate the database with a list of module 
    sessions from a CSV file, or to randomly generate module sessions for testing purposes. This command is useful 
    for bulk importing or generating test data.

    :param help: A brief description of what the command does, which is displayed when the `help` flag is used.
    :type help: str
    """
    help = "Populates database with list of module sessions from csv"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Define the arguments that the command accepts. The command can accept a CSV file to read session data from 
        and a `--test` flag to indicate random population of module sessions for testing.

        :param parser: The argument parser for the command.
        :type parser: CommandParser
        """
        parser.add_argument("csv_file", nargs = "?", type=str, help="The CSV File to read data from")#
        parser.add_argument("--test", 
                            action="store_true", 
                            help="A boolean flag to indicate random population of class session")
        
    
    def remove_duplicates(self, skill_list):
        """Remove duplicate skills from the list, keeping the highest level skill for each unique skill name.

        :param skill_list: A list of `Skill` objects that may contain duplicates.
        :type skill_list: list
        :return: A list of unique `Skill` objects with the highest level for each skill name.
        :rtype: list
        """
        skill_dict = {}
        for skill in skill_list:
            if skill.name not in skill_dict:
                skill_dict[skill.name] = skill
            else:
                if skill.level > skill_dict[skill.name].level:
                    skill_dict[skill.name] = skill
        return list(skill_dict.values())
    
    def handle(self, *args, **options) -> str | None:
        """Handle the execution of the command. This method will either populate module sessions randomly for testing 
        if the `--test` flag is provided, or prepare to populate module sessions from a CSV file.

        :param args: Additional positional arguments.
        :type args: list
        :param options: A dictionary of options passed to the command, including the CSV file path and the `--test` flag.
        :type options: dict
        :return: A success message indicating the operation performed.
        :rtype: str or None
        """
        csv_file = options.get("csv_file", None)
        test = options["test"]
        
        if test:
            self.stdout.write(self.style.SUCCESS("Class sessions will be randomly generated"))
            call_command("delete_test_sessions")
            modules = Module.objects.all()
            for module in modules:
                SESSION_TYPE_CHOICES = ["Lecture", "Tutorial", "Lab"]
                skill_choices = list(Skill.objects.all())
                num_skills = random.randint(1,2)
                required_skill = random.sample(skill_choices, num_skills)
                required_skill = self.remove_duplicates(required_skill)
                
                num_types = random.randint(1,len(SESSION_TYPE_CHOICES))
                selected_types = random.sample(SESSION_TYPE_CHOICES, num_types)
                for session_type in selected_types:
                    if session_type == "Lecture":
                        required_demonstrator = 0
                    else:
                        required_demonstrator = random.choice([1,2])
                    
                    module_session, created = ModuleSession.objects.update_or_create(class_code=module,
                                                                                     session_type=session_type,
                                                                                     defaults={"required_demonstrator": required_demonstrator,
                                                                                               "test_session": True})
                    
                    for skill in required_skill:
                        RequirementSkill.objects.create(class_session=module_session,
                                                                  skill=skill)
                        
            
            
        
        else:
            #Add functionality here to populate from a csv file
            self.stdout.write(self.style.SUCCESS("Class sessions will be filled from CSV file"))