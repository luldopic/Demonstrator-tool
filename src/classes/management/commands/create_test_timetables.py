from django.core.management.base import BaseCommand, CommandParser
from classes.models import SessionSchedule, ModuleSession, Module
from timetable.models import Timeslot
import random
import time

MIN_LAB_DURATION = 2
MAX_LAB_DURATION = 2
TUTORIAL_DURATION = 1
LECTURE_MIN_DURATION = 1
LECTURE_MAX_DURATION = 2
MAX_TEACHING_HOURS = 12
MAX_LABS_PER_WEEK = 2
MAX_TUTORIALS_PER_WEEK = 3
MAX_LECTURES_PER_WEEK = 2

class Command(BaseCommand):
    """The `Command` class defines a custom Django management command to generate random timetables for testing purposes. 
    The command can create timetables for specific classes or all classes that need schedules, with various constraints 
    to simulate realistic teaching loads.

    :param help: A brief description of what the command does, which is displayed when the `help` flag is used.
    :type help: str
    """
    help = "Generates random timetables for testing purposes"
    
    def get_constraints(self, module: Module):
        """Retrieve the session constraints for a specific module. These constraints define the minimum and maximum 
        number of lectures, tutorials, and labs per week, as well as the maximum allowed teaching hours.

        :param module: The module for which constraints are being retrieved.
        :type module: Module
        :return: A tuple containing the constraints for lectures, tutorials, and labs.
        :rtype: tuple
        """
        session_types = module.get_session_types()
        min_lec, max_lec = (0,0)
        min_tut, max_tut = (0,0)
        min_lab, max_lab = (0,0)
        
        if session_types[0]:
            min_lec, max_lec = (1,MAX_LECTURES_PER_WEEK)
        if session_types[1]:
            min_tut, max_tut = (1,MAX_TUTORIALS_PER_WEEK)
        if session_types[2]:
            min_lab, max_lab = (1,MAX_LABS_PER_WEEK)
        
        return (min_lec, max_lec, min_tut, max_tut, min_lab, max_lab)
    
    def get_total_hours(self, timetable: list):
        """Calculate the total number of teaching hours in the given timetable.

        :param timetable: The timetable to calculate hours for.
        :type timetable: list
        :return: The total number of teaching hours.
        :rtype: int
        """
        total_hours = 0
        for session in timetable:
            total_hours += len(session["timeslots"])
        return total_hours
    
    def count_session_type(self, timetable: dict):
        """Count the number of sessions of each type (lecture, tutorial, lab) in the timetable.

        :param timetable: The timetable to analyze.
        :type timetable: dict
        :return: A tuple containing the counts of lectures, tutorials, and labs.
        :rtype: tuple
        """
        lecture_count = sum(1 for session in timetable if session["type"] == "Lecture")
        tutorial_count = sum(1 for session in timetable if session["type"] == "Tutorial")
        lab_count = sum(1 for session in timetable if session["type"] == "Lab")
        return (lecture_count, tutorial_count, lab_count)
    
    def check_max_constraints(self, timetable: list, constraints: tuple):
        """Check if the timetable exceeds the maximum constraints for lectures, tutorials, labs, and total teaching hours.

        :param timetable: The timetable to check.
        :type timetable: list
        :param constraints: The constraints to apply.
        :type constraints: tuple
        :return: `True` if the timetable meets the constraints, `False` otherwise.
        :rtype: bool
        """
        lecture_count, tutorial_count, lab_count = self.count_session_type(timetable)
        _, max_lec, _, max_tut, _, max_lab = constraints
        return (
            lecture_count <= max_lec and
            tutorial_count <= max_tut and
            lab_count <= max_lab and
            self.get_total_hours(timetable) <= MAX_TEACHING_HOURS and 
            self.check_scheduling_conflicts(timetable)
        )
    
    
    def check_constraint_fulfilled(self, timetable: dict, constraints: tuple):
        """Check if the timetable fulfills the minimum and maximum constraints for lectures, tutorials, labs, 
        and total teaching hours.

        :param timetable: The timetable to check.
        :type timetable: dict
        :param constraints: The constraints to apply.
        :type constraints: tuple
        :return: `True` if the timetable fulfills the constraints, `False` otherwise.
        :rtype: bool
        """
        lecture_count, tutorial_count, lab_count = self.count_session_type(timetable)
        min_lec, max_lec, min_tut, max_tut, min_lab, max_lab = constraints
        return (
            lecture_count >= min_lec and lecture_count <= max_lec and
            tutorial_count >= min_tut and tutorial_count <= max_tut and
            lab_count >= min_lab and lab_count <= max_lab and
            self.get_total_hours(timetable) <= MAX_TEACHING_HOURS and 
            self.check_scheduling_conflicts(timetable)
        )
    
    def check_scheduling_conflicts(self, timetable):
        """Check for any scheduling conflicts within the timetable.

        :param timetable: The timetable to check.
        :type timetable: list
        :return: `True` if there are no conflicts, `False` otherwise.
        :rtype: bool
        """
        return len(self.get_schedule(timetable)) == len(set(self.get_schedule(timetable)))
    
    def get_schedule(self, timetable):
        """Extract the schedule (list of timeslots) from the timetable.

        :param timetable: The timetable to extract the schedule from.
        :type timetable: list
        :return: A list of timeslots.
        :rtype: list
        """
        schedule = []
        for session in timetable:
            for timeslot in session["timeslots"]:
                schedule.append(timeslot)
        return schedule
    
    def get_timeslots(self, num, include_weekend):
        """Generate a list of timeslots for a session, ensuring they occur on the same day and possibly excluding weekends.

        :param num: The number of timeslots to generate.
        :type num: int
        :param include_weekend: Whether to include weekends in the timeslot selection.
        :type include_weekend: bool
        :return: A list of timeslots.
        :rtype: list
        """
        days_range = 6 if include_weekend else 4
        timeslots: list[Timeslot] = []
        all_conditions = False
        init_num = num
        while not all_conditions:
            timeslots.clear()
            first_timeslot = Timeslot.get_random_slot()
            timeslot_allowed = True
            while first_timeslot.day >= days_range:  # ensure first timeslot is within allowed days
                first_timeslot = Timeslot.get_random_slot()
            timeslots.append(first_timeslot)
            timeslot_allowed = True
            num = init_num
            while num > 1:
                next_timeslot = timeslots[-1].get_next()
                if next_timeslot is None:
                    break
                timeslots.append(next_timeslot)
                num -= 1
            all_conditions = Timeslot.are_same_day(timeslots) and timeslot_allowed
        return timeslots
    
    def add_lecture(self, timetable: list, include_weekend):
        """Add a lecture session to the timetable.

        :param timetable: The timetable to add the lecture to.
        :type timetable: list
        :param include_weekend: Whether to include weekends in the lecture timeslot selection.
        :type include_weekend: bool
        """
        class_time = random.randint(LECTURE_MIN_DURATION,LECTURE_MAX_DURATION)
        timetable.append({"type":"Lecture",
                          "timeslots": self.get_timeslots(class_time,include_weekend)})
    
    def add_tutorial(self, timetable: list, include_weekend):
        """Add a tutorial session to the timetable.

        :param timetable: The timetable to add the tutorial to.
        :type timetable: list
        :param include_weekend: Whether to include weekends in the tutorial timeslot selection.
        :type include_weekend: bool
        """
        class_time = TUTORIAL_DURATION
        timetable.append({"type":"Tutorial",
                          "timeslots": self.get_timeslots(class_time,include_weekend)})
        
    def add_lab(self, timetable: list, include_weekend):
        """Add a lab session to the timetable.

        :param timetable: The timetable to add the lab to.
        :type timetable: list
        :param include_weekend: Whether to include weekends in the lab timeslot selection.
        :type include_weekend: bool
        """
        class_time = random.randint(MIN_LAB_DURATION, MAX_LAB_DURATION)
        timetable.append({"type":"Lab",
                          "timeslots": self.get_timeslots(class_time,include_weekend)})
    
    def assign_timeslots(self, constraints: tuple, class_timetable: list = [], include_weekend: bool = False):
        """Assign timeslots to the sessions in the timetable, ensuring that constraints are met.

        :param constraints: The constraints to apply.
        :type constraints: tuple
        :param class_timetable: The timetable to assign timeslots to.
        :type class_timetable: list, optional
        :param include_weekend: Whether to include weekends in the timeslot selection.
        :type include_weekend: bool
        :return: The updated timetable with assigned timeslots.
        :rtype: list
        """
        remaining_types = ["Lecture", "Tutorial", "Lab"]
        while not self.check_constraint_fulfilled(class_timetable, constraints):
            #print(self.count_session_type(class_timetable))           
            session_type = random.choice(remaining_types)
            initial_timetable = class_timetable[:]
            
            if session_type == "Lecture":
                self.add_lecture(class_timetable, include_weekend)
            elif session_type == "Tutorial":
                self.add_tutorial(class_timetable, include_weekend)
            elif session_type == "Lab":
                self.add_lab(class_timetable, include_weekend)

            if not self.check_max_constraints(class_timetable, constraints):
                class_timetable = initial_timetable
        
        return class_timetable
        
    def create_schedule(self, module: Module, timetable: dict):
        """Create session schedules based on the generated timetable and save them to the database.

        :param module: The module for which the schedule is being created.
        :type module: Module
        :param timetable: The generated timetable with session types and timeslots.
        :type timetable: dict
        """
        for session in timetable:
            for timeslot in session["timeslots"]:
                SessionSchedule.objects.create(
                    class_session=ModuleSession.objects.get(class_code=module, session_type=session["type"]),
                    timeslot=timeslot
                )
        
    
    def add_arguments(self, parser: CommandParser):
        """Define the arguments that the command accepts. The command can accept a class code to generate a schedule 
        for a specific module, an option to generate schedules for all modules that require them, and options 
        to include weekends and set a random seed.

        :param parser: The argument parser for the command.
        :type parser: CommandParser
        """
        parser.add_argument(
            '--class-code',
            type=str,
            help='Specify the class code for which the schedule needs to be created'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Specify to create schedules for all classes with no schedules'
        )
        
        parser.add_argument(
            "--include-weekend",
            action="store_true",
            help = 'Include weekends in the generated schedule'
        )
        
        parser.add_argument(
            "--debug-seed",
            type=int,
            help='Set a random seed for debugging purposes'
        )
    def handle(self, *args, **kwargs):
        """Handle the command execution, generating timetables based on the provided options. The method will 
        create schedules for either a specific module or all modules, with an option to include weekends in the scheduling.

        :param args: Additional positional arguments.
        :type args: list
        :param kwargs: A dictionary of options passed to the command.
        :type kwargs: dict
        :return: None
        """
        class_code = kwargs.get('class_code')
        all_classes = kwargs.get('all')
        include_weekend = kwargs.get('include_weekend')
        debug_seed = kwargs.get('debug_seed')
        
        if debug_seed is not None:
            random.seed(debug_seed)
        else:
            debug_seed = int(time.time())
            random.seed(debug_seed)
            self.stdout.write(self.style.NOTICE(f'Random seed used: {debug_seed}'))
            SessionSchedule.objects.filter(class_session__test_session=True).delete()
        
        if class_code:
            modules = Module.objects.filter(class_code=class_code)
        elif all_classes:
            modules = Module.objects.filter(modulesession__test_session=True).distinct()
        else:
            self.stdout.write(self.style.ERROR('Please provide either --class-code or --all option'))
            return
        
        for module in modules:
            constraints = self.get_constraints(module)
            timetable = self.assign_timeslots(constraints, [], include_weekend=include_weekend)
            self.create_schedule(module, timetable)
            self.stdout.write(self.style.SUCCESS(f'Schedule created for module: {module.class_code}'))