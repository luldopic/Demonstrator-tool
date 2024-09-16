from django.db.models import Q
from allocations.models import Allocation, AllocationDomain
from users.models import Demonstrator
from allocations.utils.constraint_manager import HardConstraintManager, PrimaryConstraintManager, SecondaryConstraintManager
import random

class AllocationManager:
    """The `AllocationManager` class provides a set of static methods for managing and allocating demonstrators to 
    various allocations based on a series of constraints. The allocation process involves filtering demonstrators 
    through a series of hard, primary, secondary, and tertiary soft constraints to find the most suitable candidates 
    for each allocation.

    The class includes methods for retrieving unallocated objects, filtering demonstrators based on different levels 
    of constraints, and assigning demonstrators through various allocation strategies.

    This class interacts with several models including `Allocation`, `AllocationDomain`, and `Demonstrator`, and utilizes 
    constraint managers to enforce the constraints during allocation.

    :param allocation: An instance of the `Allocation` model representing the current allocation for which demonstrators 
        need to be assigned.
    :type allocation: `Allocation`
    """
    @staticmethod
    def get_unallocated():
        """Retrieve all allocations that have not yet been assigned to a demonstrator.

        :return: A queryset of `Allocation` objects where `demonstrator` is `None`.
        :rtype: QuerySet
        """
        return Allocation.objects.filter(demonstrator__isnull=True)
        
    @staticmethod
    def get_demonstrators_by_hard_constraints(allocation):
        """Filter demonstrators by applying hard constraints to an allocation.

        :param allocation: The allocation for which demonstrators need to be filtered.
        :type allocation: `Allocation`
        :return: A list of demonstrators that satisfy all hard constraints for the given allocation.
        :rtype: list of `Demonstrator`
        """
        valid_demonstrators = Demonstrator.objects.all()
        valid_demonstrators = [dem for dem in valid_demonstrators if
                               True and
                               #Add Constraints here
                               HardConstraintManager.is_demonstrator_not_double_booked(allocation) and
                               HardConstraintManager.is_demonstator_available_for_all(allocation) and
                               HardConstraintManager.is_allocation_not_previously_approved(allocation)]
        return valid_demonstrators
    
    @staticmethod
    def get_demonstrators_by_primary_soft_constraints(allocation):
        """Filter demonstrators by applying primary soft constraints after applying hard constraints.

        :param allocation: The allocation for which demonstrators need to be filtered.
        :type allocation: `Allocation`
        :return: A list of demonstrators that satisfy both hard and primary soft constraints for the given allocation.
        :rtype: list of `Demonstrator`
        """
        valid_demonstrators = AllocationManager.get_demonstrators_by_hard_constraints(allocation)
        valid_demonstrators = [dem for dem in valid_demonstrators if
                               True and
                               #Add Constraints here
                               PrimaryConstraintManager.demonstrator_has_beginner_skill(allocation, dem)]
        return valid_demonstrators
    
    @staticmethod
    def get_demonstrators_by_secondary_soft_constraints(allocation):
        """Filter demonstrators by applying secondary soft constraints after applying primary soft constraints.

        :param allocation: The allocation for which demonstrators need to be filtered.
        :type allocation: `Allocation`
        :return: A list of demonstrators that satisfy hard, primary, and secondary soft constraints for the given allocation.
        :rtype: list of `Demonstrator`
        """
        valid_demonstrators = AllocationManager.get_demonstrators_by_primary_soft_constraints(allocation)
        valid_demonstrators = [dem for dem in valid_demonstrators if
                               True and
                               #Add Constraints here
                               SecondaryConstraintManager.demonstrator_has_skill_or_higher(allocation, dem)]
        return valid_demonstrators
    
    @staticmethod
    def get_demonstrators_by_tertiary_soft_constraints(allocation):
        """Filter demonstrators by applying tertiary soft constraints after applying secondary soft constraints.

        :param allocation: The allocation for which demonstrators need to be filtered.
        :type allocation: `Allocation`
        :return: A list of demonstrators that satisfy hard, primary, secondary, and tertiary soft constraints for the given allocation.
        :rtype: list of `Demonstrator`
        """
        valid_demonstrators = AllocationManager.get_demonstrators_by_secondary_soft_constraints(allocation)
        valid_demonstrators = [dem for dem in valid_demonstrators if
                               True
                               #Add Constraints here
                               ]
        return valid_demonstrators
    
    @staticmethod
    def get_solution_domain(allocation):
        """Generate and save the solution domain for a given allocation, including demonstrators filtered by 
        hard and soft constraints.

        :param allocation: The allocation for which the solution domain needs to be generated.
        :type allocation: `Allocation`
        """
        allocation_domain = AllocationDomain(allocation = allocation)
        allocation_domain.save()
        
        hard_constraint_demonstrators = AllocationManager.get_demonstrators_by_hard_constraints(allocation)
        primary_soft_constraint_demonstrators = AllocationManager.get_demonstrators_by_primary_soft_constraints(allocation)
        secondary_soft_constraint_demonstrators = AllocationManager.get_demonstrators_by_secondary_soft_constraints(allocation)
        tertiary_soft_constraint_demonstrators = AllocationManager.get_demonstrators_by_tertiary_soft_constraints(allocation)
        
        allocation_domain.hard_constraint_demonstrators.set(hard_constraint_demonstrators)
        allocation_domain.primary_soft_constraint_demonstrators.set(primary_soft_constraint_demonstrators)
        allocation_domain.secondary_soft_constraint_demonstrators.set(secondary_soft_constraint_demonstrators)
        allocation_domain.tertiary_soft_constraint_demonstrators.set(tertiary_soft_constraint_demonstrators)
        
        allocation_domain.save()
    
    @staticmethod
    def allocate_with_constraints(allocation):
        """Attempt to allocate a demonstrator to the allocation by applying constraints from harshest to least harsh.

        :param allocation: The allocation to be fulfilled.
        :type allocation: `Allocation`
        :return: `True` if a demonstrator is successfully allocated, `False` otherwise.
        :rtype: bool
        """
        if AllocationManager.try_allocate_with_tertiary_constraints(allocation):
            return True
        elif AllocationManager.try_allocate_with_secondary_constraints(allocation):
            return True
        elif AllocationManager.try_allocate_with_primary_constraints(allocation):
            return True
        else:
            return False
    
    @staticmethod
    def try_allocate_with_tertiary_constraints(allocation):
        """Attempt to allocate a demonstrator by applying tertiary soft constraints.

        :param allocation: The allocation to be fulfilled.
        :type allocation: `Allocation`
        :return: `True` if a demonstrator is successfully allocated, `False` otherwise.
        :rtype: bool
        """
        valid_demonstrators = AllocationManager.get_demonstrators_by_tertiary_soft_constraints(allocation)
        return AllocationManager.try_allocation(allocation, valid_demonstrators)

    @staticmethod
    def try_allocate_with_secondary_constraints(allocation):
        """Attempt to allocate a demonstrator by applying secondary soft constraints.

        :param allocation: The allocation to be fulfilled.
        :type allocation: `Allocation`
        :return: `True` if a demonstrator is successfully allocated, `False` otherwise.
        :rtype: bool
        """
        valid_demonstrators = AllocationManager.get_demonstrators_by_secondary_soft_constraints(allocation)
        return AllocationManager.try_allocation(allocation, valid_demonstrators)

    @staticmethod
    def try_allocate_with_primary_constraints(allocation):
        """Attempt to allocate a demonstrator by applying primary soft constraints.

        :param allocation: The allocation to be fulfilled.
        :type allocation: `Allocation`
        :return: `True` if a demonstrator is successfully allocated, `False` otherwise.
        :rtype: bool
        """
        valid_demonstrators = AllocationManager.get_demonstrators_by_primary_soft_constraints(allocation)
        return AllocationManager.try_allocation(allocation, valid_demonstrators)
    
    @staticmethod
    def try_allocation(allocation, valid_demonstrators):
        """Try to allocate one of the valid demonstrators to the allocation. The allocation is saved if 
        successful.

        :param allocation: The allocation to be fulfilled.
        :type allocation: `Allocation`
        :param valid_demonstrators: A list of demonstrators that satisfy the necessary constraints.
        :type valid_demonstrators: list of `Demonstrator`
        :return: `True` if a demonstrator is successfully allocated, `False` otherwise.
        :rtype: bool
        """
        for demonstrator in valid_demonstrators:
            allocation.demonstrator = demonstrator
            if HardConstraintManager.is_demonstrator_not_double_booked(allocation) and \
               HardConstraintManager.is_demonstator_available_for_all(allocation) and \
               HardConstraintManager.is_allocation_not_previously_approved(allocation):
                allocation.save()
                return True
        allocation.demonstrator = None
        return False
    
    @staticmethod
    def backtracking(queryset):
        """Perform backtracking to allocate demonstrators to unallocated allocations within the queryset.

        :param queryset: A queryset of allocations to be fulfilled.
        :type queryset: QuerySet
        :return: `True` if all allocations are successfully assigned, `False` otherwise.
        :rtype: bool
        """
        unallocated_allocations = queryset.filter(demonstrator__isnull=True)
        for allocation in unallocated_allocations:
            if not AllocationManager.allocate_with_constraints(allocation):
                return False
        return True
    
    @staticmethod
    def assign_demonstrators(queryset):
        """Assign demonstrators to allocations in the provided queryset by applying the backtracking algorithm.

        :param queryset: A queryset of allocations to be fulfilled.
        :type queryset: QuerySet
        :return: `True` if all allocations are successfully assigned and approved, `False` otherwise.
        :rtype: bool
        """
        res = AllocationManager.backtracking(queryset)
        if res:
            for allocation in queryset:
                allocation.approved = True
                allocation.save()
            return True
        return False
    
    
    @staticmethod
    def batch_allocate(batch_size : float):
        """Batch allocate demonstrators to allocations by dividing unallocated objects into batches.

        :param batch_size: The number of allocations to process in each batch.
        :type batch_size: float
        """
        unallocated = AllocationManager.get_unallocated()
        
        to_allocate = list(unallocated)
        random.shuffle(to_allocate)
        
        batches = []
        while to_allocate:
            batch = []
            for _ in range(min(batch_size, len(to_allocate))):
                batch.append(to_allocate.pop())
            batches.append(batch)
            
        for batch in batches:
            ids = [instance.pk for instance in batch]
            queryset = Allocation.objects.filter(pk__in=ids)
            AllocationManager.assign_demonstrators(queryset)