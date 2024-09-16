from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.contrib import admin
from allocations.models import Allocation
from classes.admin import ModuleSessionAdmin
from classes.models import ModuleSession
from allocations.utils.goodness_of_fit import GoodnessOfFit
from allocations.utils.allocation_manager import AllocationManager
import math
import time

class StrategyTests(TestCase):
    """The `StrategyTests` class contains test cases for various allocation strategies in the Django application.

    :param setUpTestData: Sets up the test data at the class level, including creating a superuser, populating default timeslots, skills, modules, sessions, and timetables.
    :type setUpTestData: Class Method
    :param generate_demonstrators: Generates a specified number of demonstrators based on a multiplier.
    :type generate_demonstrators: Static Method
    :param setUp: Initializes the test environment for each test case, including logging in as the admin user and resetting allocations.
    :type setUp: Method
    :param time_for_allocation: Measures and returns the time taken for batch allocation.
    :type time_for_allocation: Static Method
    :param test_double_ratio_single_size: Tests the allocation strategy with a double demonstrator ratio and single batch size.
    :type test_double_ratio_single_size: Method
    :param test_double_ratio_one_size: Tests the allocation strategy with a double demonstrator ratio and 1% batch size.
    :type test_double_ratio_one_size: Method
    :param test_double_ratio_five_size: Tests the allocation strategy with a double demonstrator ratio and 5% batch size.
    :type test_double_ratio_five_size: Method
    :param test_double_ratio_ten_size: Tests the allocation strategy with a double demonstrator ratio and 10% batch size.
    :type test_double_ratio_ten_size: Method
    :param test_double_ratio_twenty_size: Tests the allocation strategy with a double demonstrator ratio and 20% batch size.
    :type test_double_ratio_twenty_size: Method
    :param test_equal_ratio_single_size: Tests the allocation strategy with an equal demonstrator ratio and single batch size.
    :type test_equal_ratio_single_size: Method
    :param test_equal_ratio_one_size: Tests the allocation strategy with an equal demonstrator ratio and 1% batch size.
    :type test_equal_ratio_one_size: Method
    :param test_equal_ratio_five_size: Tests the allocation strategy with an equal demonstrator ratio and 5% batch size.
    :type test_equal_ratio_five_size: Method
    :param test_equal_ratio_ten_size: Tests the allocation strategy with an equal demonstrator ratio and 10% batch size.
    :type test_equal_ratio_ten_size: Method
    :param test_equal_ratio_twenty_size: Tests the allocation strategy with an equal demonstrator ratio and 20% batch size.
    :type test_equal_ratio_twenty_size: Method
    :param test_half_ratio_single_size: Tests the allocation strategy with a half demonstrator ratio and single batch size.
    :type test_half_ratio_single_size: Method
    :param test_half_ratio_one_size: Tests the allocation strategy with a half demonstrator ratio and 1% batch size.
    :type test_half_ratio_one_size: Method
    :param test_half_ratio_five_size: Tests the allocation strategy with a half demonstrator ratio and 5% batch size.
    :type test_half_ratio_five_size: Method
    :param test_half_ratio_ten_size: Tests the allocation strategy with a half demonstrator ratio and 10% batch size.
    :type test_half_ratio_ten_size: Method
    :param test_half_ratio_twenty_size: Tests the allocation strategy with a half demonstrator ratio and 20% batch size.
    :type test_half_ratio_twenty_size: Method
    :param test_quarter_ratio_single_size: Tests the allocation strategy with a quarter demonstrator ratio and single batch size.
    :type test_quarter_ratio_single_size: Method
    :param test_quarter_ratio_one_size: Tests the allocation strategy with a quarter demonstrator ratio and 1% batch size.
    :type test_quarter_ratio_one_size: Method
    :param test_quarter_ratio_five_size: Tests the allocation strategy with a quarter demonstrator ratio and 5% batch size.
    :type test_quarter_ratio_five_size: Method
    :param test_quarter_ratio_ten_size: Tests the allocation strategy with a quarter demonstrator ratio and 10% batch size.
    :type test_quarter_ratio_ten_size: Method
    :param test_quarter_ratio_twenty_size: Tests the allocation strategy with a quarter demonstrator ratio and 20% batch size.
    :type test_quarter_ratio_twenty_size: Method
    """
    @classmethod
    def setUpTestData(cls) -> None:
        """Set up the test data once for the entire test class."""
        User = get_user_model()
        User.objects.create_superuser(username='admin', email='admin@example.com', password='admin')
        call_command("populate_default_timeslots")
        call_command("populate_test_skills","test_data/skills.csv")
        call_command("populate_modules",  "test_data/CIS_modules.csv")
        call_command("populate_sessions", "--test")
        call_command("create_test_timetables",  "--all")
        
        ## Get batch sizes
        cls.total = Allocation.objects.all().count()
        cls.batch_size = [1]
        for n in [1,5,10,20]:
            cls.batch_size.append(math.ceil((n*cls.total)/100))
    
    """
    Strategies
    Demonstrator: Allocation Slot Ratio -> Double, Equal, Half (2,1,0.5)
    BatchSize -> 1, 1%, 5%, 10%, 20%
    """
    
    @staticmethod
    def generate_demonstrators(multiplier):
        """Generate a specific number of demonstrators based on the multiplier."""
        num_demonstrator = math.ceil(StrategyTests.total * multiplier)
        call_command("generate_test_users", demonstrator = num_demonstrator)
        call_command("populate_competencies", "--test")
        
    def setUp(self):
        """Set up the test environment for each test case."""
        self.client.login(username='admin', password='admin')
        Allocation.objects.all().delete()
        module_session_admin = ModuleSessionAdmin(model=ModuleSession, admin_site=admin.site)
        
        request = self.client.request().wsgi_request
        queryset = ModuleSession.objects.all()
        module_session_admin.ensure_correct_allocation(request, queryset)
    
    @staticmethod
    def time_for_allocation(batch_num):
        """Measure and return the time taken for batch allocation."""
        print("Allocation Start")
        start_time = time.time()
        AllocationManager.batch_allocate(StrategyTests.batch_size[batch_num])
        end_time = time.time()
        print(f"Allocation Complete in {end_time-start_time} seconds")
        return end_time-start_time
        
    #Double
    def test_double_ratio_single_size(self):
        StrategyTests.generate_demonstrators(2)
        elapsed_time = StrategyTests.time_for_allocation(0)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_doubleratio_singlesize_report.txt', 'w') as file:
            file.write(report)
    
    def test_double_ratio_one_size(self):
        StrategyTests.generate_demonstrators(2)
        elapsed_time = StrategyTests.time_for_allocation(1)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_doubleratio_onesize_report.txt', 'w') as file:
            file.write(report)
    
    def test_double_ratio_five_size(self):
        StrategyTests.generate_demonstrators(2)
        elapsed_time = StrategyTests.time_for_allocation(2)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_doubleratio_fivesize_report.txt', 'w') as file:
            file.write(report)
    
    def test_double_ratio_ten_size(self):
        StrategyTests.generate_demonstrators(2)
        elapsed_time = StrategyTests.time_for_allocation(3)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_doubleratio_tensize_report.txt', 'w') as file:
            file.write(report)
    
    def test_double_ratio_twenty_size(self):
        StrategyTests.generate_demonstrators(2)
        elapsed_time = StrategyTests.time_for_allocation(4)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_doubleratio_twentysize_report.txt', 'w') as file:
            file.write(report)
            
    #Equal
    def test_equal_ratio_single_size(self):
        StrategyTests.generate_demonstrators(1)
        elapsed_time = StrategyTests.time_for_allocation(0)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_equalratio_singlesize_report.txt', 'w') as file:
            file.write(report)
    
    def test_equal_ratio_one_size(self):
        StrategyTests.generate_demonstrators(1)
        elapsed_time = StrategyTests.time_for_allocation(1)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_equalratio_onesize_report.txt', 'w') as file:
            file.write(report)
            
    def test_equal_ratio_five_size(self):
        StrategyTests.generate_demonstrators(1)
        elapsed_time = StrategyTests.time_for_allocation(2)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_equalratio_fivesize_report.txt', 'w') as file:
            file.write(report)
    
    def test_equal_ratio_ten_size(self):
        StrategyTests.generate_demonstrators(1)
        elapsed_time = StrategyTests.time_for_allocation(3)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_equalratio_tensize_report.txt', 'w') as file:
            file.write(report)
    
    def test_equal_ratio_twenty_size(self):
        StrategyTests.generate_demonstrators(1)
        elapsed_time = StrategyTests.time_for_allocation(4)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_equalratio_twentysize_report.txt', 'w') as file:
            file.write(report)
    
    #Half
    def test_half_ratio_single_size(self):
        StrategyTests.generate_demonstrators(0.5)
        elapsed_time = StrategyTests.time_for_allocation(0)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_halfratio_singlesize_report.txt', 'w') as file:
            file.write(report)
    
    def test_half_ratio_one_size(self):
        StrategyTests.generate_demonstrators(0.5)
        elapsed_time = StrategyTests.time_for_allocation(1)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_halfratio_onesize_report.txt', 'w') as file:
            file.write(report)
    
    def test_half_ratio_five_size(self):
        StrategyTests.generate_demonstrators(0.5)
        elapsed_time = StrategyTests.time_for_allocation(2)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_halfratio_fivesize_report.txt', 'w') as file:
            file.write(report)
            
    def test_half_ratio_ten_size(self):
        StrategyTests.generate_demonstrators(0.5)
        elapsed_time = StrategyTests.time_for_allocation(3)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_halfratio_tensize_report.txt', 'w') as file:
            file.write(report)
            
    def test_half_ratio_twenty_size(self):
        StrategyTests.generate_demonstrators(0.5)
        elapsed_time = StrategyTests.time_for_allocation(4)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_halfratio_twentysize_report.txt', 'w') as file:
            file.write(report)
    
    #Quarter
    def test_quarter_ratio_single_size(self):
        StrategyTests.generate_demonstrators(0.25)
        elapsed_time = StrategyTests.time_for_allocation(0)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_quarterratio_singlesize_report.txt', 'w') as file:
            file.write(report)
    
    def test_quarter_ratio_one_size(self):
        StrategyTests.generate_demonstrators(0.25)
        elapsed_time = StrategyTests.time_for_allocation(1)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_quarterratio_onesize_report.txt', 'w') as file:
            file.write(report)
    
    def test_quarter_ratio_five_size(self):
        StrategyTests.generate_demonstrators(0.25)
        elapsed_time = StrategyTests.time_for_allocation(2)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_quarterratio_fivesize_report.txt', 'w') as file:
            file.write(report)
            
    def test_half_ratio_ten_size(self):
        StrategyTests.generate_demonstrators(0.25)
        elapsed_time = StrategyTests.time_for_allocation(3)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_quarterratio_tensize_report.txt', 'w') as file:
            file.write(report)
            
    def test_half_ratio_twenty_size(self):
        StrategyTests.generate_demonstrators(0.25)
        elapsed_time = StrategyTests.time_for_allocation(4)
        report, results_dict = GoodnessOfFit.generate_report(elapsed_time)
        print(report)
        with open('test_quarterratio_twentysize_report.txt', 'w') as file:
            file.write(report)

