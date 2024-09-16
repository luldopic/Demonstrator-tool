from django.core.management.base import BaseCommand, CommandParser
from django.core.management import call_command
from classes.models import Skill, Competency
from users.models import Demonstrator
import csv, random
import numpy as np


class Command(BaseCommand):
    """The `Command` class defines a custom Django management command to populate the database with a list of competencies 
    from a CSV file or to randomly generate competencies for test purposes. This command is useful for bulk data 
    population and testing scenarios.

    :param help: A brief description of what the command does, which is displayed when the `help` flag is used.
    :type help: str
    """
    help = "Populates database with list of competencies from csv"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Define the arguments that the command accepts. The command can accept a CSV file to read competencies from 
        and a `--test` flag to indicate random population of competencies for testing.

        :param parser: The argument parser for the command.
        :type parser: CommandParser
        """
        parser.add_argument("csv_file", nargs = "?", type=str, help="The CSV File to read data from")#
        parser.add_argument("--test", 
                            action="store_true", 
                            help="A boolean flag to indicate random population of dependencies")
        
    
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
    
    def biased_skill_level(self):
        """Generate a biased random skill level using a geometric distribution, with a higher probability of lower levels.

        :return: A skill level, where the maximum level is 2.
        :rtype: int
        """
        p = 0.7  
        max_level = 2
        level = min(np.random.geometric(p) - 1, max_level)
        return level
    
    def handle(self, *args, **options) -> str | None:
        """Handle the execution of the command. This method will either populate competencies randomly for test demonstrators 
        if the `--test` flag is provided, or prepare to populate competencies from a CSV file.

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
            self.stdout.write(self.style.SUCCESS("Competencies will be randomly generated"))
            fake_demonstrators = Demonstrator.objects.filter(user__is_fake=True)
            for demonstrator in fake_demonstrators:
                Competency.objects.filter(demonstrator=demonstrator).delete()
            skill_choices = list(Skill.objects.all())
            mean_skill = 5
            stdev_skill = 2
            for demonstrator in fake_demonstrators:
                num_skills = min(max(1, int(np.random.normal(mean_skill, stdev_skill))), len(skill_choices))
                selected_skills = random.sample(skill_choices, num_skills)
                selected_skills = self.remove_duplicates(selected_skills)
                for skill in selected_skills:
                    skill_level = self.biased_skill_level()
                    skill_name = skill.name
                    competency_skill = Skill.objects.get(name= skill_name, level = skill_level)
                    Competency.objects.create(demonstrator=demonstrator, skill=competency_skill)
                
            
            
        
        else:
            #Add functionality here to populate from a csv file
            self.stdout.write(self.style.SUCCESS("Competencies will be filled from CSV file"))