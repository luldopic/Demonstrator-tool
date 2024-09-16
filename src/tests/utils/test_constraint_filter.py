from django.test import TestCase
from unittest.mock import MagicMock, patch
from allocations.utils import constraint_manager as cm
from allocations.models import Allocation, AllocationDomain
from classes.models import Module, ModuleSession, Skill, RequirementSkill, Competency, SessionSchedule
from timetable.models import Timeslot, Semester
from users.models import Demonstrator, User, UserAvailability
from allocations.utils.constraint_filter import ConstrantFilterQuery

class ConstrantFilterQueryTests(TestCase):
    """The `ConstrantFilterQueryTests` class contains test cases for the `ConstrantFilterQuery` utility class used in the Django application.

    :param setUp: Initializes the test environment, including creating instances of `User`, `Demonstrator`, `Timeslot`, `UserAvailability`, `Module`, `ModuleSession`, `Skill`, `RequirementSkill`, `Competency`, and `Allocation`.
    :type setUp: Method
    :param test_filter_allocations_by_hard_constraints: Tests the `filter_allocations_by_hard_constraints` method to ensure it correctly filters allocations based on hard constraints.
    :type test_filter_allocations_by_hard_constraints: Method
    :param test_filter_allocation_by_primary_soft_constraints: Tests the `filter_allocation_by_primary_soft_constraints` method to ensure it correctly filters allocations based on primary soft constraints.
    :type test_filter_allocation_by_primary_soft_constraints: Method
    :param test_filter_allocation_by_secondary_soft_constraints: Tests the `filter_allocation_by_secondary_soft_constraints` method to ensure it correctly filters allocations based on secondary soft constraints.
    :type test_filter_allocation_by_secondary_soft_constraints: Method
    """

    def setUp(self):
        # Setup mock data and mock the constraint manager methods
        self.user1 = User.objects.create(username="user1", is_demonstrator=True, email = "test1@test.com")
        self.user2 = User.objects.create(username="user2", is_demonstrator=True, email = "test2@test.com")
        self.user3 = User.objects.create(username="user3", is_demonstrator=True, email = "test3@test.com")
        timeslot = Timeslot.objects.create(day = 0, start_time = "09:00", end_time = "10:00")
        UserAvailability.objects.create(user = self.user1, timeslot = timeslot)
        UserAvailability.objects.create(user = self.user2, timeslot = timeslot)
        UserAvailability.objects.create(user = self.user3, timeslot = timeslot)

        self.demo1 = Demonstrator.objects.get(user=self.user1)
        self.demo2 = Demonstrator.objects.get(user=self.user2)
        self.demo3 = Demonstrator.objects.get(user=self.user3)
        
        self.semester = Semester.objects.create(year = 2024, semester = 2)
        self.module = Module.objects.create(class_code='test', name='Test Module', semester=self.semester)
        self.session = ModuleSession.objects.create(class_code = self.module, session_type = "test", required_demonstrator = 3)
        SessionSchedule.objects.create(class_session = self.session, timeslot = timeslot)
        
        Skill.objects.create(name="Test Skill")
        skill = Skill.objects.all().first()
        RequirementSkill.objects.create(class_session = self.session, skill = skill)
        Competency.objects.create(demonstrator = self.demo1, skill = skill)
        Competency.objects.create(demonstrator = self.demo2, skill = skill)
        Competency.objects.create(demonstrator = self.demo3, skill = skill)
        
        self.allocation1 = Allocation.objects.create(demonstrator=self.demo1, class_session=self.session)
        self.allocation2 = Allocation.objects.create(demonstrator=self.demo2, class_session=self.session)
        self.allocation3 = Allocation.objects.create(demonstrator=self.demo3, class_session=self.session)
        

    @patch.object(cm.HardConstraintManager, 'is_demonstrator_not_double_booked', return_value=True)
    @patch.object(cm.HardConstraintManager, 'is_demonstator_available_for_all', return_value=True)
    @patch.object(cm.HardConstraintManager, 'is_allocation_not_previously_approved', return_value=True)
    def test_filter_allocations_by_hard_constraints(self):
        queryset = Allocation.objects.all()
        result = ConstrantFilterQuery.filter_allocations_by_hard_constraints(queryset)
        expected_ids = sorted([self.allocation1.id, self.allocation2.id, self.allocation3.id])
        result_ids = sorted([alloc.id for alloc in result])
        self.assertEqual(result_ids, expected_ids)

    @patch.object(cm.PrimaryConstraintManager, 'demonstrator_has_beginner_skill', return_value=True)
    @patch.object(cm.PrimaryConstraintManager,  'session_has_half_demonstrators' , return_value=True)
    def test_filter_allocation_by_primary_soft_constraints(self):
        queryset = Allocation.objects.all()
        result = ConstrantFilterQuery.filter_allocation_by_primary_soft_constraints(queryset)
        expected_ids = sorted([self.allocation1.id, self.allocation2.id, self.allocation3.id])
        result_ids = sorted([alloc.id for alloc in result])
        self.assertEqual(result_ids, expected_ids)

    def test_filter_allocation_by_secondary_soft_constraints(self):
        queryset = Allocation.objects.all()
        result = ConstrantFilterQuery.filter_allocation_by_secondary_soft_constraints(queryset)
        expected_ids = sorted([self.allocation1.id, self.allocation2.id, self.allocation3.id])
        result_ids = sorted([alloc.id for alloc in result])
        self.assertEqual(result_ids, expected_ids)