from django.test import TestCase
from unittest.mock import patch, MagicMock
from allocations.models import Allocation, AllocationDomain
from users.models import Demonstrator, User
from timetable.models import Timeslot
from allocations.utils import constraint_manager as cm
from allocations.utils.allocation_manager import AllocationManager

class AllocationManagerTests(TestCase):

    def setUp(self):
        # Create mock users and demonstrators
        self.user1 = User.objects.create(username="user1", is_demonstrator=True, email = "test1@test.com")
        self.user2 = User.objects.create(username="user2", is_demonstrator=True, email = "test1@test.com")
        self.user3 = User.objects.create(username="user3", is_demonstrator=True, email = "test1@test.com")

        self.demo1 = Demonstrator.objects.create(user=self.user1)
        self.demo2 = Demonstrator.objects.create(user=self.user2)
        self.demo3 = Demonstrator.objects.create(user=self.user3)

        self.timeslot = Timeslot.objects.create(day=0, start_time="09:00", end_time="10:00")

        self.allocation1 = Allocation.objects.create(demonstrator=self.demo1, class_session=None, approved=False)
        self.allocation2 = Allocation.objects.create(demonstrator=None, class_session=None, approved=False)
        self.allocation3 = Allocation.objects.create(demonstrator=None, class_session=None, approved=False)

    def tearDown(self):
        Allocation.objects.all().delete()
        Demonstrator.objects.all().delete()
        User.objects.all().delete()

    def test_get_unallocated(self):
        unallocated = AllocationManager.get_unallocated()
        self.assertQuerysetEqual(
            unallocated, 
            [self.allocation2, self.allocation3],
            transform=lambda x: x
        )

    @patch.object(cm.HardConstraintManager, 'is_demonstrator_not_double_booked', return_value=True)
    @patch.object(cm.HardConstraintManager, 'is_demonstator_available_for_all', return_value=True)
    @patch.object(cm.HardConstraintManager, 'is_allocation_not_previously_approved', return_value=True)
    def test_get_demonstrators_by_hard_constraints(self, mock1, mock2, mock3):
        valid_demonstrators = AllocationManager.get_demonstrators_by_hard_constraints(self.allocation2)
        self.assertListEqual(valid_demonstrators, [self.demo1, self.demo2, self.demo3])

    @patch.object(cm.PrimaryConstraintManager, 'demonstrator_has_beginner_skill', return_value=True)
    def test_get_demonstrators_by_primary_soft_constraints(self, mock_primary_skill):
        valid_demonstrators = AllocationManager.get_demonstrators_by_primary_soft_constraints(self.allocation2)
        self.assertListEqual(valid_demonstrators, [self.demo1, self.demo2, self.demo3])

    @patch.object(cm.SecondaryConstraintManager, 'demonstrator_has_skill_or_higher', return_value=True)
    def test_get_demonstrators_by_secondary_soft_constraints(self, mock_secondary_skill):
        valid_demonstrators = AllocationManager.get_demonstrators_by_secondary_soft_constraints(self.allocation2)
        self.assertListEqual(valid_demonstrators, [self.demo1, self.demo2, self.demo3])

    @patch.object(AllocationManager, 'get_demonstrators_by_hard_constraints', return_value=[])
    @patch.object(AllocationManager, 'get_demonstrators_by_primary_soft_constraints', return_value=[])
    @patch.object(AllocationManager, 'get_demonstrators_by_secondary_soft_constraints', return_value=[])
    def test_get_solution_domain(self, mock_hard, mock_primary, mock_secondary):
        AllocationManager.get_solution_domain(self.allocation2)
        allocation_domain = AllocationDomain.objects.get(allocation=self.allocation2)
        self.assertEqual(allocation_domain.hard_constraint_demonstrators.count(), 0)
        self.assertEqual(allocation_domain.primary_soft_constraint_demonstrators.count(), 0)
        self.assertEqual(allocation_domain.secondary_soft_constraint_demonstrators.count(), 0)

    @patch.object(AllocationManager, 'try_allocate_with_tertiary_constraints', return_value=True)
    def test_allocate_with_constraints(self, mock_allocate):
        self.assertTrue(AllocationManager.allocate_with_constraints(self.allocation2))
        mock_allocate.assert_called_once_with(self.allocation2)

    @patch.object(AllocationManager, 'backtracking', return_value=True)
    def test_assign_demonstrators(self, mock_backtracking):
        queryset = Allocation.objects.all()
        self.assertTrue(AllocationManager.assign_demonstrators(queryset))
        self.assertTrue(self.allocation1.approved)
        self.assertTrue(self.allocation2.approved)
        self.assertTrue(self.allocation3.approved)
