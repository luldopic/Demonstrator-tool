from django.test import TestCase
from unittest.mock import patch, MagicMock
from users.models import User, Demonstrator, Lecturer
from allocations.models import Allocation, AllocationDomain
from classes.models import ModuleSession, Module
from timetable.models import Semester

class AllocationModelTest(TestCase):
    """The `AllocationModelTest` class contains test cases for the `Allocation` model in the Django application.

    :param setUp: Initializes the test environment, creating instances of `Demonstrator`, `Semester`, `Lecturer`, `Module`, `ModuleSession`, and `Allocation`.
    :type setUp: Method
    :param test_create_allocation: Tests the creation of an `Allocation` instance, verifying that it is saved correctly and associated with the correct `Demonstrator` and `ModuleSession`.
    :type test_create_allocation: Method
    :param test_allocate_demonstrator_to_null: Tests the behavior of the `Allocation` model when the `Demonstrator` field is set to `None`.
    :type test_allocate_demonstrator_to_null: Method
    :param test_demonstrator_deletion: Tests the behavior of the `Allocation` model when the associated `Demonstrator` is deleted.
    :type test_demonstrator_deletion: Method
    :param test_class_session_deletion: Tests the behavior of the `Allocation` model when the associated `ModuleSession` is deleted.
    :type test_class_session_deletion: Method
    """
    def setUp(self):
        self.demonstrator = Demonstrator.objects.create(user=User.objects.create_user(username="demo", password="password", email= "demo@test.com"))
        self.semester = Semester.objects.create(year="2023/2024", semester=0, start_date="2023-09-01", end_date="2024-01-15")
        self.lecturer = Lecturer.objects.create(user=User.objects.create_user(username="lecturer", password="password", email="lec@test.com"))
        self.module = Module.objects.create(class_code="CS101", name="Computer Science 101", lecturer=self.lecturer, semester=self.semester)
        self.module_session = ModuleSession.objects.create(class_code=self.module, session_type="Lab")
        self.allocation = Allocation.objects.create(demonstrator=self.demonstrator, class_session=self.module_session, approved=False)

    def test_create_allocation(self):
        self.assertIsNotNone(self.allocation.pk)
        self.assertEqual(self.allocation.demonstrator, self.demonstrator)
        self.assertEqual(self.allocation.class_session, self.module_session)
        self.assertFalse(self.allocation.approved)

    def test_allocate_demonstrator_to_null(self):
        self.allocation.demonstrator = None
        self.allocation.save()
        self.assertFalse(self.allocation.approved)

    def test_demonstrator_deletion(self):
        self.demonstrator.delete()
        self.allocation.refresh_from_db()
        self.assertIsNone(self.allocation.demonstrator)
        self.assertFalse(self.allocation.approved)

    def test_class_session_deletion(self):
        self.module_session.delete()
        self.assertFalse(Allocation.objects.filter(pk=self.allocation.pk).exists())

class AllocationDomainModelTest(TestCase):
    """The `AllocationDomainModelTest` class contains test cases for the `AllocationDomain` model in the Django application.

    :param setUp: Initializes the test environment, creating instances of `Demonstrator`, `Lecturer`, `Semester`, `Module`, `ModuleSession`, `Allocation`, and `AllocationDomain`.
    :type setUp: Method
    :param test_create_allocation_domain: Tests the creation of an `AllocationDomain` instance, verifying that it is saved correctly and associated with the correct `Allocation`.
    :type test_create_allocation_domain: Method
    :param test_add_hard_constraint_demonstrator: Tests adding a `Demonstrator` to the hard constraints of an `AllocationDomain`.
    :type test_add_hard_constraint_demonstrator: Method
    :param test_add_primary_soft_constraint_demonstrator: Tests adding a `Demonstrator` to the primary soft constraints of an `AllocationDomain`.
    :type test_add_primary_soft_constraint_demonstrator: Method
    :param test_add_secondary_soft_constraint_demonstrator: Tests adding a `Demonstrator` to the secondary soft constraints of an `AllocationDomain`.
    :type test_add_secondary_soft_constraint_demonstrator: Method
    :param test_add_tertiary_soft_constraint_demonstrator: Tests adding a `Demonstrator` to the tertiary soft constraints of an `AllocationDomain`.
    :type test_add_tertiary_soft_constraint_demonstrator: Method
    """
    def setUp(self):
        self.demonstrator = Demonstrator.objects.create(user=User.objects.create_user(username="demo", password="password", email= "demo@test.com"))
        self.lecturer = Lecturer.objects.create(user=User.objects.create_user(username="lecturer", password="password", email= "lec@test.com"))
        self.semester = Semester.objects.create(year="2023/2024", semester=0, start_date="2023-09-01", end_date="2024-01-15")
        self.module = Module.objects.create(class_code="CS101", name="Computer Science 101", lecturer=self.lecturer, semester=self.semester)
        self.module_session = ModuleSession.objects.create(class_code=self.module, session_type="Lab")
        self.allocation = Allocation.objects.create(demonstrator=self.demonstrator, class_session=self.module_session)
        self.allocation_domain = AllocationDomain.objects.create(allocation=self.allocation)

    def test_create_allocation_domain(self):
        self.assertIsNotNone(self.allocation_domain.pk)
        self.assertEqual(self.allocation_domain.allocation, self.allocation)

    def test_add_hard_constraint_demonstrator(self):
        self.allocation_domain.hard_constraint_demonstrators.add(self.demonstrator)
        self.assertIn(self.demonstrator, self.allocation_domain.hard_constraint_demonstrators.all())

    def test_add_primary_soft_constraint_demonstrator(self):
        self.allocation_domain.primary_soft_constraint_demonstrators.add(self.demonstrator)
        self.assertIn(self.demonstrator, self.allocation_domain.primary_soft_constraint_demonstrators.all())

    def test_add_secondary_soft_constraint_demonstrator(self):
        self.allocation_domain.secondary_soft_constraint_demonstrators.add(self.demonstrator)
        self.assertIn(self.demonstrator, self.allocation_domain.secondary_soft_constraint_demonstrators.all())

    def test_add_tertiary_soft_constraint_demonstrator(self):
        self.allocation_domain.tertiary_soft_constraint_demonstrators.add(self.demonstrator)
        self.assertIn(self.demonstrator, self.allocation_domain.tertiary_soft_constraint_demonstrators.all())

class AllocationSignalTest(TestCase):
    """The `AllocationSignalTest` class contains test cases for signals related to the `Allocation` model in the Django application.

    :param setUp: Initializes the test environment, creating instances of `Demonstrator`, `Lecturer`, `Semester`, `Module`, `ModuleSession`, `Allocation`, and `AllocationDomain`.
    :type setUp: Method
    :param test_demonstrator_deletion_signal: Tests that the appropriate signal is sent and handled when a `Demonstrator` is deleted, ensuring that related `Allocation` instances are updated correctly.
    :type test_demonstrator_deletion_signal: Method
    """
    def setUp(self):
        self.demonstrator = Demonstrator.objects.create(user=User.objects.create_user(username="demo", password="password", email= "demo@test.com"))
        self.lecturer = Lecturer.objects.create(user=User.objects.create_user(username="lecturer", password="password", email= "lec@test.com"))
        self.semester = Semester.objects.create(year="2023/2024", semester=0, start_date="2023-09-01", end_date="2024-01-15")
        self.module = Module.objects.create(class_code="CS101", name="Computer Science 101", lecturer=self.lecturer, semester=self.semester)
        self.module_session = ModuleSession.objects.create(class_code=self.module, session_type="Lab")
        self.allocation = Allocation.objects.create(demonstrator=self.demonstrator, class_session=self.module_session)
        self.allocation_domain = AllocationDomain.objects.create(allocation=self.allocation)


    @patch('allocations.models.Allocation.objects.filter')
    def test_demonstrator_deletion_signal(self, mock_filter):
        mock_filter.return_value.update.return_value = None
        self.demonstrator.delete()
        mock_filter.assert_called_with(demonstrator=self.demonstrator)
        mock_filter.return_value.update.assert_called_with(approved=False)