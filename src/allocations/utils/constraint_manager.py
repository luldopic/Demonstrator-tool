from allocations.models import Allocation
from users.models import UserAvailability, Demonstrator
from classes.models import Competency, RequirementSkill, Module, ModuleSession
from math import ceil

class ConstraintManager:
    """The `ConstraintManager` class is a base class for managing constraints during the allocation of demonstrators 
    to various sessions. This class serves as the foundation for more specific constraint managers that handle 
    both hard and soft constraints.

    This class does not implement any functionality directly but provides a structure for subclasses to enforce 
    constraints on allocations.

    :param allocation: An instance of the `Allocation` model representing the current allocation being processed.
    :type allocation: `Allocation`
    """

class HardConstraintManager(ConstraintManager):
    """The `HardConstraintManager` class is responsible for enforcing hard constraints during the allocation process. 
    These constraints ensure that no demonstrator is double booked, that demonstrators are fully available for 
    the sessions they are assigned to, and that previously approved allocations are not modified.

    This class provides static methods that check specific hard constraints on allocations.

    :param allocation: An instance of the `Allocation` model representing the current allocation being processed.
    :type allocation: `Allocation`
    """
    
    @staticmethod
    def is_demonstrator_not_double_booked(allocation: Allocation, dem = None) -> bool:
        """Check if the demonstrator assigned to the allocation is not double booked. 

        :param allocation: The allocation to check.
        :type allocation: `Allocation`
        :param dem: An optional specific demonstrator to check. If `None`, the method checks the demonstrator assigned to the allocation.
        :type dem: `Demonstrator`, optional
        :return: `True` if the demonstrator is not double booked, `False` otherwise.
        :rtype: bool
        """
        if dem == None:
            demonstrator = allocation.demonstrator
        else:
            demonstrator = dem
        if demonstrator == None:
            return True
        all_allocations = Allocation.objects.filter(
            demonstrator=demonstrator
        ).exclude(id=allocation.id)
        current_session_timeslots = set(allocation.class_session.get_timeslots())
        
        for existing_allocation in all_allocations:
            existing_timeslots = set(existing_allocation.class_session.get_timeslots())
            if current_session_timeslots & existing_timeslots:
                return False
        
        return True
        
    
    @staticmethod
    def is_demonstator_available_for_all(allocation: Allocation, dem = None) -> bool:
        """Check if the demonstrator assigned to the allocation is available for all timeslots of the session.

        :param allocation: The allocation to check.
        :type allocation: `Allocation`
        :param dem: An optional specific demonstrator to check. If `None`, the method checks the demonstrator assigned to the allocation.
        :type dem: `Demonstrator`, optional
        :return: `True` if the demonstrator is available for all timeslots, `False` otherwise.
        :rtype: bool
        """
        if dem == None:
            demonstrator = allocation.demonstrator
        else:
            demonstrator = dem
        if demonstrator == None:
            return True
        timeslots = allocation.class_session.get_timeslots()
        is_available_for_all = all(
            UserAvailability.objects.get(user = demonstrator.user, timeslot=timeslot).is_available 
            for timeslot in timeslots
                                            
        )
        return is_available_for_all
    
    @staticmethod
    def is_allocation_not_previously_approved(allocation: Allocation) -> bool:
        """Check if the allocation has not been previously approved.

        :param allocation: The allocation to check.
        :type allocation: `Allocation`
        :return: `True` if the allocation is not previously approved, `False` otherwise.
        :rtype: bool
        """
        return not allocation.approved

class SoftConstraintManager(ConstraintManager):
    """The `SoftConstraintManager` class serves as a base class for enforcing soft constraints during the allocation process. 
    Soft constraints can include primary, secondary, and tertiary constraints that provide additional flexibility 
    compared to hard constraints.

    This class provides utility methods and serves as the base for more specific soft constraint managers.

    :param allocation: An instance of the `Allocation` model representing the current allocation being processed.
    :type allocation: `Allocation`
    """
    @staticmethod
    def is_subset(list1, list2):
        """Check if `list1` is a subset of `list2`.

        :param list1: The list to check as a subset.
        :type list1: list
        :param list2: The list to check against.
        :type list2: list
        :return: `True` if `list1` is a subset of `list2`, `False` otherwise.
        :rtype: bool
        """
        return set(list1).issubset(set(list2))

class PrimaryConstraintManager(SoftConstraintManager):
    """The `PrimaryConstraintManager` class handles primary soft constraints during the allocation process. 
    These constraints include ensuring that sessions have at least half of the required demonstrators and 
    that all demonstrators meet the minimum skill requirements.

    This class provides static methods that enforce primary soft constraints on allocations.

    :param allocation: An instance of the `Allocation` model representing the current allocation being processed.
    :type allocation: `Allocation`
    """    
    @staticmethod
    def session_has_half_demonstrators(allocation: Allocation) -> bool:
        """Check if the session associated with the allocation has at least half of the required number of demonstrators.

        :param allocation: The allocation to check.
        :type allocation: `Allocation`
        :return: `True` if the session has at least half the required number of demonstrators, `False` otherwise.
        :rtype: bool
        """
        module_session: ModuleSession = allocation.class_session
        session_allocations = Allocation.objects.filter(class_session = module_session,
                                                        demonstrator__isnull = False).count()
        required_number = module_session.required_demonstrator
        half_required = ceil(required_number/2)
        return session_allocations >= half_required
    
    @staticmethod
    def demonstrator_has_beginner_skill(allocation: Allocation, dem = None) -> bool:
        """Check if the demonstrator assigned to the allocation has at least a beginner skill level in the required skills.

        :param allocation: The allocation to check.
        :type allocation: `Allocation`
        :param dem: An optional specific demonstrator to check. If `None`, the method checks the demonstrator assigned to the allocation.
        :type dem: `Demonstrator`, optional
        :return: `True` if the demonstrator has the required beginner skills, `False` otherwise.
        :rtype: bool
        """
        if dem == None:
            demonstrator = allocation.demonstrator
        else:
            demonstrator = dem
        
        required_skills = RequirementSkill.objects.filter(class_session = allocation.class_session)
        demonstrator_competencies = Competency.objects.filter(demonstrator = demonstrator)
        
        skill_list = [skill.skill.name for skill in required_skills]
        competency_list = [competency.skill.name for competency in demonstrator_competencies]
        
        return SoftConstraintManager.is_subset(skill_list, competency_list)
        
class SecondaryConstraintManager(SoftConstraintManager):
    """The `SecondaryConstraintManager` class handles secondary soft constraints during the allocation process. 
    These constraints ensure that sessions have the exact number of required demonstrators and that the demonstrators 
    meet or exceed the skill level required for the session.

    This class provides static methods that enforce secondary soft constraints on allocations.

    :param allocation: An instance of the `Allocation` model representing the current allocation being processed.
    :type allocation: `Allocation`
    """
    
    @staticmethod
    def session_has_all_demonstrators(allocation: Allocation) -> bool:
        """Check if the session associated with the allocation has the exact number of required demonstrators.

        :param allocation: The allocation to check.
        :type allocation: `Allocation`
        :return: `True` if the session has the required number of demonstrators, `False` otherwise.
        :rtype: bool
        """
        module_session: ModuleSession = allocation.class_session
        session_allocations = Allocation.objects.filter(class_session = module_session,
                                                        demonstrator__isnull = False).count()
        required_number = module_session.required_demonstrator
        return session_allocations == required_number
    
    @staticmethod
    def demonstrator_has_skill_or_higher(allocation: Allocation, dem = None) -> bool:
        """Check if the demonstrator assigned to the allocation meets or exceeds the required skill level.

        :param allocation: The allocation to check.
        :type allocation: `Allocation`
        :param dem: An optional specific demonstrator to check. If `None`, the method checks the demonstrator assigned to the allocation.
        :type dem: `Demonstrator`, optional
        :return: `True` if the demonstrator has the required skill level or higher, `False` otherwise.
        :rtype: bool
        """
        if dem == None:
            demonstrator = allocation.demonstrator
        else:
            demonstrator = dem
        required_skills = RequirementSkill.objects.filter(class_session = allocation.class_session)
        demonstrator_competencies = Competency.objects.filter(demonstrator = demonstrator)
        
        competency_dict = {comp.skill.name: comp.skill.level for comp in demonstrator_competencies}
        
        for required_skill in required_skills:
            skill_name = required_skill.skill.name
            skill_level = required_skill.skill.level
            if skill_name not in competency_dict or competency_dict[skill_name] < skill_level:
                return False
        
        return True
        
class TertiaryConstraintManager(SoftConstraintManager):
    """The `TertiaryConstraintManager` class is intended to handle tertiary soft constraints during the allocation process. 
    These constraints may include preferences such as assigning the lecturer's preferred demonstrator or 
    ensuring demonstrators meet the required skill level.

    This class currently serves as a placeholder for future implementations of tertiary constraints.

    :param allocation: An instance of the `Allocation` model representing the current allocation being processed.
    :type allocation: `Allocation`
    """
    pass