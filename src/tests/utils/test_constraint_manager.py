import tests
from django.test import TestCase
from faker import Faker
from datetime import time
from allocations.models import Allocation
from users.models import UserAvailability, Demonstrator, User
from classes.models import Competency, RequirementSkill, Module, ModuleSession, SessionSchedule, Skill
from timetable.models import Timeslot, Semester
from allocations.utils import constraint_manager as cm
from django.db.models import Q

class BaseConstraintManagerTest(TestCase):
    """The `BaseConstraintManagerTest` class provides the foundational setup for all constraint manager-related tests, including the creation of test users, demonstrators, timeslots, skills, competencies, and module sessions.

    :param setUp: Initializes the test environment with mock data for users, demonstrators, skills, competencies, timeslots, user availability, and module sessions.
    :type setUp: Method
    """
    def setUp(self):
        User.objects.all().delete()
        Demonstrator.objects.all().delete()      
        """
        Test Timeslots
        0: Day 0, 0900, 1000
        1: Day 0, 1000, 1100
        2: Day 0, 1100, 1200
        3: Day 0, 1200, 1300
        """
        timeslots = {}
        for i in range(4):
            timeslots[i] = Timeslot.objects.create(day = 0,
                                                   start_time = time(hour=i+9),
                                                   end_time = time(hour=i+10))
        
        """
        Test Skills
        1-3: Skill 1 (Beginner -> Expert)
        4-6: Skill 2 (Beginner -> Expert)
        Key (name,level)
        """
        skills = {}
        for i, skill_name in enumerate(["Skill1", "Skill2"]):
            skill_set = Skill.objects.create(name = skill_name)
            for skill in skill_set:
                skills[(skill_name,skill.level)] = skill
    
        """
        Test Demonstrators
        Dem 0: Expert at Skill 1, Available (1,2,3,4)
        Dem 1: Beginner at Skill 1, Available (1,2,3,4)
        Dem 2: Intermediate at Skill 1, Available (1,2,3,4)
        Dem 3: Expert at Skill 1 and 2, Available (1,2,3,4)
        Dem 3: Beginner at Skill 1 and 2, Available (1,2,3,4)
        Dem 4: Expert at Skill 2, Available  (1,2,3,4)
        Dem 5: Expert at Skill 1, Available (-,-,-,-)
        Dem 6: Expert at Skill 1, Available (1,2,-,-)
        Dem 7: Expert at Skill 1, Available (1,-,-,-)
        Dem 8: Expert at Skill 1, Available (-,-,3,4)
        Dem 9: Expert at Skill 1 and 2, Available (1,2,3,4) pre-allocated
        """
        faker = Faker()
        users = {}
        self.dems = {}
        for i in range(10):
            users[i] = User.objects.create(
                username = faker.user_name(),
                email = faker.email(),
                first_name = faker.first_name(),
                last_name = faker.last_name(),
                is_demonstrator = True
            )
            self.dems[i] = Demonstrator.objects.get(user = users[i])

        """
        Assigning UserAvailability and Competency
        """
        dem_attributes = {
            0: [(0,1,2,3), [("Skill1", 2)]],
            1: [(0,1,2,3), [("Skill1", 0)]],
            2: [(0,1,2,3), [("Skill1", 1)]],
            3: [(0,1,2,3), [("Skill1", 2), ("Skill2", 2)]],
            4: [(0,1,2,3), [("Skill1", 0), ("Skill2", 0)]],
            5: [(0,1,2,3), [("Skill2", 2)]],
            6: [(), [("Skill1", 2)]],
            7: [(0,1), [("Skill1", 2)]],
            8: [(0,), [("Skill1", 2)]],
            9: [(0,3), [("Skill1", 2)]],
            10: [(0,1,2,3), [("Skill1", 2), ("Skill2", 2)]],
        }
        
        UserAvailability.objects.all().delete()
        for dem_key in self.dems.keys():
            #Assigning UserAvailability
            for timeslot_key in timeslots.keys():
                user_availability, created = UserAvailability.objects.get_or_create(user=users[dem_key],
                                                                                    timeslot=timeslots[timeslot_key]
                )
                if timeslot_key in dem_attributes[dem_key][0]:
                    pass
                else:
                    user_availability.is_available=False
                    user_availability.save()
                    
            
            #Assigning Competency
            for skill in dem_attributes[dem_key][1]:
                Competency.objects.create(skill = skills[skill],
                                          demonstrator = self.dems[dem_key])
        
        """
        Test Module Sessions
        0: Requires ("Skill1",2). Scheduled at (1,2) Requires 1 Demonstrator(s)
        1: Requires ("Skill1",2). Scheduled at (1,2) Requires 2 Demonstrator(s)
        2: Requires ("Skill1",0). Scheduled at (1,2) Requires 1 Demonstrator(s)
        3: Requires ("Skill1",0). Scheduled at (1,2) Requires 2 Demonstrator(s)
        4: Requires ("Skill1",2) and ("Skill2",2). Scheduled at (1,2) Requires 1 Demonstrator(s)
        5: Requires ("Skill1",2) and ("Skill2",2). Scheduled at (1,2) Requires 2 Demonstrator(s)
        6: Requires ("Skill1",0) and ("Skill2",0). Scheduled at (1,2) Requires 1 Demonstrator(s)
        7: Requires ("Skill1",0) and ("Skill2",0). Scheduled at (1,2) Requires 2 Demonstrator(s)
        
        pre_assigned: Requires Requires ("Skill1",2). Scheduled at (1,2,3,4) Requires 1 Demonstrator(s). Assigned to Dem 9
        """
        module_attributes = {
            0: ([("Skill1",2)],1),
            1: ([("Skill1",2)],2),
            2: ([("Skill1",0)],1),
            3: ([("Skill1",0)],2),
            4: ([("Skill1",2),("Skill2",2)],1),
            5: ([("Skill1",2),("Skill2",2)],2),
            6: ([("Skill1",0),("Skill2",0)],1),
            7: ([("Skill1",0),("Skill2",0)],2)
        }
        
        self.semester = Semester.objects.create(year = 2024, semester = 2)
        self.module = Module.objects.create(class_code='test', name='Test Module', semester=self.semester)

        
        self.module_sessions = {}
        for session in module_attributes.keys():
            self.module_sessions[session] = ModuleSession.objects.create(class_code = self.module,
                                                                        session_type = "test",
                                                                        required_demonstrator = module_attributes[session][1])
            
            #Create skill requirements
            for skill in module_attributes[session][0]:
                RequirementSkill.objects.create(class_session = self.module_sessions[session],
                                                skill = skills[skill])
            
            #Create Session Schedule
            for timeslot in range(2):
                SessionSchedule.objects.create(class_session = self.module_sessions[session],
                                               timeslot = timeslots[timeslot])
        
        #Creating pre-assigned
        self.pre_assigned = ModuleSession.objects.create(class_code = self.module,
                                                        session_type = "test",
                                                        required_demonstrator = 1)
        RequirementSkill.objects.create(class_session = self.pre_assigned,
                                        skill = skills[("Skill1",2)])
        for timeslot in range(2):
                SessionSchedule.objects.create(class_session = self.pre_assigned,
                                               timeslot = timeslots[timeslot])
        
        pre_assigned = Allocation.objects.get(class_session = self.pre_assigned)
        pre_assigned.demonstrator = self.dems[9]
        pre_assigned.approved = True
        pre_assigned.save()
        
    
                
            

class ConstraintManagerTest(BaseConstraintManagerTest):
    """The `ConstraintManagerTest` class inherits from `BaseConstraintManagerTest` and serves as a placeholder for future tests related to constraint management."""
    pass

class HardConstraintManagerTest(BaseConstraintManagerTest):
    """The `HardConstraintManagerTest` class contains test cases for the `HardConstraintManager` in the `constraint_manager` module.

    :param setUp: Re-initializes the test environment with mock data.
    :type setUp: Method
    :param test_is_demonstrator_not_booked_normal: Tests if a demonstrator is not double-booked under normal circumstances.
    :type test_is_demonstrator_not_booked_normal: Method
    :param test_is_demonstrator_not_booked_same_module_session: Tests if a demonstrator is double-booked when assigned to multiple allocations within the same module session.
    :type test_is_demonstrator_not_booked_same_module_session: Method
    :param test_is_demonstrator_not_booked_different_session_same_time: Tests if a demonstrator is double-booked when assigned to different module sessions at the same time.
    :type test_is_demonstrator_not_booked_different_session_same_time: Method
    :param test_is_demonstrator_available_for_all_normal: Tests if a demonstrator is available for all timeslots in a normal scenario.
    :type test_is_demonstrator_available_for_all_normal: Method
    :param test_is_demonstrator_available_for_all_partial: Tests if a demonstrator is partially available for the timeslots.
    :type test_is_demonstrator_available_for_all_partial: Method
    :param test_is_demonstrator_available_for_all_not_available: Tests if a demonstrator is not available for the required timeslots.
    :type test_is_demonstrator_available_for_all_not_available: Method
    :param test_is_allocation_not_previously_approved_Normal: Tests if an allocation has not been previously approved under normal circumstances.
    :type test_is_allocation_not_previously_approved_Normal: Method
    :param test_is_allocation_not_previously_approved_already_approved: Tests if an allocation has already been approved and correctly identified.
    :type test_is_allocation_not_previously_approved_already_approved: Method
    """
    def setUp(self) -> None:
        super().setUp()
    
    def test_is_demonstrator_not_booked_normal(self):
        #Normal case - Demonstrator 0 assigned to Allocation 1 (tied to Module session 0)
        allocations = Allocation.objects.filter(class_session = self.module_sessions[0])
        for allocation in allocations:
            allocation.demonstrator = self.dems[0]
            allocation.save()
            
        for allocation in allocations:
            result = cm.HardConstraintManager.is_demonstrator_not_double_booked(allocation)
            self.assertTrue(result)
        
    def test_is_demonstrator_not_booked_same_module_session(self):
        #Edge Case 1: Demonstrator 0 is assigned to Allocation 1 and 2 (tied to module session 1)
        allocations = Allocation.objects.filter(class_session = self.module_sessions[1])
        for allocation in allocations:
            allocation.demonstrator = self.dems[0]
            allocation.save()
            
        for allocation in allocations:
            result = cm.HardConstraintManager.is_demonstrator_not_double_booked(allocation)
            self.assertFalse(result)    
        
    def test_is_demonstrator_not_booked_different_session_same_time(self):
        #Edge Case 2: Demonstrator 0 is assigned to Allocation 1 of module session 0 and 2)
        allocations = Allocation.objects.filter(
            Q(class_session = self.module_sessions[0])| Q(class_session = self.module_sessions[2]))
        for allocation in allocations:
            allocation.demonstrator = self.dems[0]
            allocation.save()
            
        for allocation in allocations:
            result = cm.HardConstraintManager.is_demonstrator_not_double_booked(allocation)
            self.assertFalse(result)    
            
    def test_is_demonstrator_available_for_all_normal(self):
        #Normal case - Demonstrator 0 assigned to Allocation 1 (tied to Module session 0)
        allocations = Allocation.objects.filter(class_session = self.module_sessions[0])
        for allocation in allocations:
            allocation.demonstrator = self.dems[0]
            allocation.save()
            
        for allocation in allocations:
            result = cm.HardConstraintManager.is_demonstator_available_for_all(allocation)
            self.assertTrue(result)
    
    def test_is_demonstrator_available_for_all_partial(self):
        #Edge case 1 - Demonstrator 7 assigned to Allocation 1 (tied to Module session 0)
        allocations = Allocation.objects.filter(class_session = self.module_sessions[0])
        for allocation in allocations:
            allocation.demonstrator = self.dems[8]
            allocation.save()
            
        for allocation in allocations:
            result = cm.HardConstraintManager.is_demonstator_available_for_all(allocation)
            self.assertFalse(result)
    
    def test_is_demonstrator_available_for_all_not_available(self):
        #Edge case 2 - Demonstrator 5 assigned to Allocation 1 (tied to Module session 0)
        allocations = Allocation.objects.filter(class_session = self.module_sessions[0])
        for allocation in allocations:
            allocation.demonstrator = self.dems[6]
            allocation.save()
            
        for allocation in allocations:
            result = cm.HardConstraintManager.is_demonstator_available_for_all(allocation)
            self.assertFalse(result)
    
    def test_is_allocation_not_previously_approved_Normal(self):
        #Normal - Demonstrator 0 assigned to Allocation 1 (tied to Module session 0)
        allocations = Allocation.objects.filter(class_session = self.module_sessions[0])
        for allocation in allocations:
            allocation.demonstrator = self.dems[0]
            allocation.save()
            
        for allocation in allocations:
            result = cm.HardConstraintManager.is_allocation_not_previously_approved(allocation)
            self.assertTrue(result)
            
    def test_is_allocation_not_previously_approved_already_approved(self):
        #Edge Case - Demonstrator 0 assigned to Allocation 1 (tied to pre_assigned)
        allocations = Allocation.objects.filter(class_session = self.pre_assigned)
        for allocation in allocations:
            allocation.demonstrator = self.dems[0]
            allocation.save()
            
        for allocation in allocations:
            result = cm.HardConstraintManager.is_allocation_not_previously_approved(allocation)
            self.assertFalse(result)

class SoftConstraintManageTest(BaseConstraintManagerTest):
    """The `SoftConstraintManagerTest` class contains test cases for the `SoftConstraintManager` in the `constraint_manager` module.

    :param test_is_subset: Tests the `is_subset` method to ensure it correctly identifies if one list is a subset of another.
    :type test_is_subset: Method
    """
    def test_is_subset(self):
        # Subset scenario
        list1 = ["Skill1", "Skill2"]
        list2 = ["Skill1", "Skill2", "Skill3"]
        self.assertTrue(cm.SoftConstraintManager.is_subset(list1, list2))
        
        # Not a subset scenario
        list1 = ["Skill1", "Skill4"]
        list2 = ["Skill1", "Skill2", "Skill3"]
        self.assertFalse(cm.SoftConstraintManager.is_subset(list1, list2))

class PrimaryConstraintManagerTest(BaseConstraintManagerTest):
    """The `PrimaryConstraintManagerTest` class contains test cases for the `PrimaryConstraintManager` in the `constraint_manager` module.

    :param setUp: Re-initializes the test environment with mock data.
    :type setUp: Method
    :param test_session_has_half_demonstrator_normal: Tests if a session has at least half of the required demonstrators under normal circumstances.
    :type test_session_has_half_demonstrator_normal: Method
    :param test_session_has_half_demonstrator_edge: Tests the edge case where no demonstrators are assigned, but required demonstrators are more than zero.
    :type test_session_has_half_demonstrator_edge: Method
    :param test_demonstrator_has_beginner_skill_normal: Tests if a demonstrator has the beginner skill under normal circumstances.
    :type test_demonstrator_has_beginner_skill_normal: Method
    :param test_demonstrator_has_beginner_skill_edge: Tests the edge case where a demonstrator does not possess the required skill.
    :type test_demonstrator_has_beginner_skill_edge: Method
    """  
    def setUp(self) -> None:
        super().setUp()
    
    def test_session_has_half_demonstrator_normal(self):
        #Normal case 1 - Demonstrator 0 assigned to Allocation 1 (tied to Module session 0)
        allocations = Allocation.objects.filter(class_session = self.module_sessions[0])
        for allocation in allocations:
            allocation.demonstrator = self.dems[0]
            allocation.save()
            
        for allocation in allocations:
            result = cm.PrimaryConstraintManager.session_has_half_demonstrators(allocation)
            self.assertTrue(result)
            
        #Normal case 2 - Demonstrator 0 assigned to Allocation 1 (tied to Module session 1)
        allocations = Allocation.objects.filter(class_session = self.module_sessions[1])
        
        allocation = allocations.first()
        allocation.demonstrator = self.dems[0]
        allocation.save()
        
        for allocation in allocations:
            result = cm.PrimaryConstraintManager.session_has_half_demonstrators(allocation)
            self.assertTrue(result)
            
        #Normal case 3 - Demonstrator 0 and 1 assigned to Allocation 1 and 2 (tied to Module session 1)
        allocations = Allocation.objects.filter(class_session = self.module_sessions[1])
        
        for i in range(len(allocations)):
            allocations[i].demonstrator = self.dems[i]
            allocations[i].save()
        
        for allocation in allocations:
            result = cm.PrimaryConstraintManager.session_has_half_demonstrators(allocation)
            self.assertTrue(result)
    
    def test_session_has_half_demonstrator_edge(self):
        # Edge Case 1 - No demonstrators assigned, but required is more than zero
        allocations = Allocation.objects.filter(class_session=self.module_sessions[1])
        for allocation in allocations:
            allocation.demonstrator = None
            allocation.save()
        
        for allocation in allocations:
            result = cm.PrimaryConstraintManager.session_has_half_demonstrators(allocation)
            self.assertFalse(result)
        
        
    
    def test_demonstrator_has_beginner_skill_normal(self):
        # Normal case 1: Demonstrator with beginner skill
        allocation = Allocation.objects.create(class_session=self.module_sessions[0])
        allocation.demonstrator = self.dems[1]
        allocation.save()
        self.assertTrue(cm.PrimaryConstraintManager.demonstrator_has_beginner_skill(allocation))
        # Normal case 2: Demonstrator with intermediate skill
        allocation.demonstrator = self.dems[2] 
        allocation.save()
        self.assertTrue(cm.PrimaryConstraintManager.demonstrator_has_beginner_skill(allocation))
        # Normal case 3: Demonstrator with expert skill
        allocation.demonstrator = self.dems[0] 
        allocation.save()
        self.assertTrue(cm.PrimaryConstraintManager.demonstrator_has_beginner_skill(allocation))
        # Normal case 4: Demonstrator with beginner skill in both skill and module requires both
        allocation = Allocation.objects.create(class_session=self.module_sessions[4])
        allocation.demonstrator = self.dems[4] 
        allocation.save()
        self.assertTrue(cm.PrimaryConstraintManager.demonstrator_has_beginner_skill(allocation))
        # Normal case 5: Demonstrator with expert skill in both skill and module requires both
        allocation.demonstrator = self.dems[3] 
        allocation.save()
        self.assertTrue(cm.PrimaryConstraintManager.demonstrator_has_beginner_skill(allocation))
        

    def test_demonstrator_has_beginner_skill_edge(self):    
        # Edge case: Demonstrator without the required skill
        allocation = Allocation.objects.create(class_session=self.module_sessions[0])
        allocation.demonstrator = self.dems[5]
        allocation.save()
        self.assertFalse(cm.PrimaryConstraintManager.demonstrator_has_beginner_skill(allocation))

class SecondaryConstraintManagerTest(BaseConstraintManagerTest):
    """The `SecondaryConstraintManagerTest` class contains test cases for the `SecondaryConstraintManager` in the `constraint_manager` module.

    :param setUp: Re-initializes the test environment with mock data.
    :type setUp: Method
    :param test_has_all_demonstrator: Tests if a session has all required demonstrators.
    :type test_has_all_demonstrator: Method
    :param test_demonstrator_has_skill_or_higher: Tests if a demonstrator has the required skill level or higher.
    :type test_demonstrator_has_skill_or_higher: Method
    """ 
    def setUp(self) -> None:
        super().setUp()
    
    def test_has_all_demonstrator(self):
        #Normal case 1 - Demonstrator 0 assigned to Allocation 1 (tied to Module session 0)
        allocations = Allocation.objects.filter(class_session = self.module_sessions[0])
        for allocation in allocations:
            allocation.demonstrator = self.dems[0]
            allocation.save()
            
        for allocation in allocations:
            result = cm.SecondaryConstraintManager.session_has_all_demonstrators(allocation)
            self.assertTrue(result)
            
        #Normal case 2 - Demonstrator 0 assigned to Allocation 1 (tied to Module session 1)
        allocations = Allocation.objects.filter(class_session = self.module_sessions[1])
        
        allocation = allocations.first()
        allocation.demonstrator = self.dems[0]
        allocation.save()
        
        for allocation in allocations:
            result = cm.SecondaryConstraintManager.session_has_all_demonstrators(allocation)
            self.assertFalse(result)
            
        #Normal case 3 - Demonstrator 0 and 1 assigned to Allocation 1 and 2 (tied to Module session 1)
        allocations = Allocation.objects.filter(class_session = self.module_sessions[1])
        
        for i in range(len(allocations)):
            allocations[i].demonstrator = self.dems[i]
            allocations[i].save()
        
        for allocation in allocations:
            result = cm.SecondaryConstraintManager.session_has_all_demonstrators(allocation)
            self.assertTrue(result)
        
    def test_demonstrator_has_skill_or_higher(self):
        # Normal case 1: Demonstrator with beginner skill assigned to module requiring beginner
        allocation = Allocation.objects.create(class_session=self.module_sessions[2])
        allocation.demonstrator = self.dems[1]
        allocation.save()
        self.assertTrue(cm.SecondaryConstraintManager.demonstrator_has_skill_or_higher(allocation))
        # Normal case 2: Demonstrator with intermediate skill
        allocation.demonstrator = self.dems[2] 
        allocation.save()
        self.assertTrue(cm.SecondaryConstraintManager.demonstrator_has_skill_or_higher(allocation))
        # Normal case 3: Demonstrator with expert skill
        allocation.demonstrator = self.dems[0] 
        allocation.save()
        self.assertTrue(cm.SecondaryConstraintManager.demonstrator_has_skill_or_higher(allocation))
        
        # Normal case 4: Demonstrator with beginner skill assigned to module requiring expert
        allocation = Allocation.objects.create(class_session=self.module_sessions[0])
        allocation.demonstrator = self.dems[1]
        allocation.save()
        self.assertFalse(cm.SecondaryConstraintManager.demonstrator_has_skill_or_higher(allocation))
        # Normal case 5: Demonstrator with expert skill
        allocation.demonstrator = self.dems[0] 
        allocation.save()
        self.assertTrue(cm.SecondaryConstraintManager.demonstrator_has_skill_or_higher(allocation))
        
        # Normal case 6: Demonstrator with beginner skill in both assigned to module requiring expert in both
        allocation = Allocation.objects.create(class_session=self.module_sessions[4])
        allocation.demonstrator = self.dems[4]
        allocation.save()
        self.assertFalse(cm.SecondaryConstraintManager.demonstrator_has_skill_or_higher(allocation))
        # Normal case 7: Demonstrator with expert skill in both assigned to module requiring expert in both
        allocation.demonstrator = self.dems[3] 
        allocation.save()
        self.assertTrue(cm.SecondaryConstraintManager.demonstrator_has_skill_or_higher(allocation))
        # Normal case 8: Demonstrator with expert skill in one assigned to module requiring expert in both
        allocation.demonstrator = self.dems[0] 
        allocation.save()
        self.assertFalse(cm.SecondaryConstraintManager.demonstrator_has_skill_or_higher(allocation))

class TertiaryConstraintManagerTest(BaseConstraintManagerTest):    
    """The `TertiaryConstraintManagerTest` class serves as a placeholder for future tests related to the `TertiaryConstraintManager` in the `constraint_manager` module."""
    def setUp(self) -> None:
        super().setUp()
    
    pass