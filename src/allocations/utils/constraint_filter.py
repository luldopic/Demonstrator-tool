from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from allocations.utils import constraint_manager as cm

class ConstrantFilterQuery:
    """The `ConstrantFilterQuery` class provides a set of static methods for filtering allocations based on various 
    hard and soft constraints. These methods are used to narrow down the list of allocations to those that meet 
    specific criteria as defined by the constraint managers.

    The filtering process includes applying hard constraints, primary soft constraints, and secondary soft constraints 
    to ensure that only allocations meeting the necessary conditions are selected.

    :param queryset: A Django QuerySet containing the allocations to be filtered.
    :type queryset: QuerySet
    """
    @staticmethod
    def filter_allocations_by_hard_constraints(queryset):
        """Filter allocations by applying hard constraints. Only allocations where the demonstrator is not 
        double booked, fully available, and the allocation has not been previously approved are considered valid.

        :param queryset: The queryset of allocations to filter.
        :type queryset: QuerySet
        :return: A queryset of allocations that satisfy all hard constraints.
        :rtype: QuerySet
        """
        valid_allocations = [
            allocation.id for allocation in queryset
            if (
                cm.HardConstraintManager.is_demonstrator_not_double_booked(allocation) and
                cm.HardConstraintManager.is_demonstator_available_for_all(allocation) and
                cm.HardConstraintManager.is_allocation_not_previously_approved(allocation) and
                allocation.demonstrator != None
            )
        ]
        return queryset.filter(id__in=valid_allocations)
    
    @staticmethod
    def filter_allocations_by_hard_constraints_post_approve(queryset):
        """Filter allocations by applying hard constraints, excluding the check for previous approval. 
        This is typically used post-approval to ensure all remaining constraints are met.

        :param queryset: The queryset of allocations to filter.
        :type queryset: QuerySet
        :return: A queryset of allocations that satisfy the remaining hard constraints.
        :rtype: QuerySet
        """
        valid_allocations = [
            allocation.id for allocation in queryset
            if (
                cm.HardConstraintManager.is_demonstrator_not_double_booked(allocation) and
                cm.HardConstraintManager.is_demonstator_available_for_all(allocation) and
                allocation.demonstrator != None
            )
        ]
        return queryset.filter(id__in=valid_allocations)
    
    @staticmethod
    def filter_allocation_by_primary_soft_constraints(queryset):
        """Filter allocations by applying primary soft constraints. Valid allocations must have half of the 
        required demonstrators and must have demonstrators with beginner skill level.

        :param queryset: The queryset of allocations to filter.
        :type queryset: QuerySet
        :return: A queryset of allocations that satisfy the primary soft constraints.
        :rtype: QuerySet
        """
        valid_allocations = [
            allocation.id for allocation in queryset
            if (
                cm.PrimaryConstraintManager.session_has_half_demonstrators(allocation) and
                cm.PrimaryConstraintManager.demonstrator_has_beginner_skill(allocation) and
                allocation.demonstrator != None
            )
        ]
        return queryset.filter(id__in=valid_allocations)
    
    @staticmethod
    def filter_allocation_by_secondary_soft_constraints(queryset):
        """Filter allocations by applying secondary soft constraints. Valid allocations must have all required 
        demonstrators and demonstrators with the necessary skill level or higher.

        :param queryset: The queryset of allocations to filter.
        :type queryset: QuerySet
        :return: A queryset of allocations that satisfy the secondary soft constraints.
        :rtype: QuerySet
        """
        valid_allocations = [
            allocation.id for allocation in queryset
            if (
                cm.SecondaryConstraintManager.session_has_all_demonstrators(allocation) and
                cm.SecondaryConstraintManager.demonstrator_has_skill_or_higher(allocation) and
                allocation.demonstrator != None
            )
        ]
        return queryset.filter(id__in=valid_allocations)


class HardConstraintFilter(admin.SimpleListFilter):
    """The `HardConstraintFilter` class is a Django admin filter used to filter allocations in the admin interface 
    based on hard constraints. The filter provides options to display allocations that pass all hard constraints 
    or fail specific checks.

    :param title: The title of the filter as displayed in the admin interface.
    :type title: str
    :param parameter_name: The query parameter used in the admin interface to select the filter option.
    :type parameter_name: str
    """
    
    title = _('hard constraints')
    parameter_name = 'hard_constraints'

    def lookups(self, request, model_admin):
        """Define the filter options for the hard constraints.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param model_admin: The model admin class where this filter is applied.
        :type model_admin: ModelAdmin
        :return: A tuple of filter options.
        :rtype: tuple
        """
        return (
            ('all_pass', _('All Pass')),
            ('fail_double_book', _('Fail - Demonstrator Double Booked')),
            ('fail_demonstrator_available', _('Fail - Demonstrator not Fully Available')),
        )

    def queryset(self, request, queryset):
        """Filter the queryset of allocations based on the selected hard constraint option.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param queryset: The queryset of allocations to filter.
        :type queryset: QuerySet
        :return: A filtered queryset based on the selected hard constraint option.
        :rtype: QuerySet
        """
        if self.value() == 'all_pass':
            valid_allocations = ConstrantFilterQuery.filter_allocations_by_hard_constraints(queryset)
            return queryset.filter(id__in=valid_allocations)
        elif self.value() == 'fail_double_book':
            valid_allocations = [
                allocation.id for allocation in queryset
                if not cm.HardConstraintManager.is_demonstrator_not_double_booked(allocation)
            ]
            return queryset.filter(id__in=valid_allocations)
        elif self.value() == 'fail_demonstrator_available':
            valid_allocations = [
                allocation.id for allocation in queryset
                if not cm.HardConstraintManager.is_demonstator_available_for_all(allocation)
            ]
            return queryset.filter(id__in=valid_allocations)
        return queryset
    
class SoftPrimaryConstraintFilter(admin.SimpleListFilter):
    """The `SoftPrimaryConstraintFilter` class is a Django admin filter used to filter allocations in the admin interface 
    based on primary soft constraints. The filter provides options to display allocations that pass all primary 
    soft constraints or fail specific checks.

    :param title: The title of the filter as displayed in the admin interface.
    :type title: str
    :param parameter_name: The query parameter used in the admin interface to select the filter option.
    :type parameter_name: str
    """
    title = _("primary soft constraints")
    parameter_name = "soft_primary_constraints"

    def lookups(self, request, model_admin):
        """Define the filter options for the primary soft constraints.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param model_admin: The model admin class where this filter is applied.
        :type model_admin: ModelAdmin
        :return: A tuple of filter options.
        :rtype: tuple
        """
        return (
            ('all_pass', _('All Pass')),
            ('fail_half_demonstrator', _('Fail - Missing Demonstrators (need half)')),
            ('fail_beginner_skill', _('Fail - Demonstrator missing competence')),
        )
    
    def queryset(self, request, queryset):
        """Filter the queryset of allocations based on the selected primary soft constraint option.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param queryset: The queryset of allocations to filter.
        :type queryset: QuerySet
        :return: A filtered queryset based on the selected primary soft constraint option.
        :rtype: QuerySet
        """
        if self.value() == 'all_pass':
            valid_allocations = ConstrantFilterQuery.filter_allocation_by_primary_soft_constraints(queryset)
            return queryset.filter(id__in=valid_allocations)
        elif self.value() == 'fail_half_demonstrator':
            valid_allocations = [
                allocation.id for allocation in queryset
                if not cm.PrimaryConstraintManager.session_has_half_demonstrators(allocation)
            ]
            return queryset.filter(id__in=valid_allocations)
        elif self.value() == 'fail_beginner_skill':
            valid_allocations = [
                allocation.id for allocation in queryset
                if not cm.PrimaryConstraintManager.demonstrator_has_beginner_skill(allocation)
            ]
            return queryset.filter(id__in=valid_allocations)
        return queryset
        
class SoftSecondaryConstraintFilter(admin.SimpleListFilter):
    """The `SoftSecondaryConstraintFilter` class is a Django admin filter used to filter allocations in the admin interface 
    based on secondary soft constraints. The filter provides options to display allocations that pass all secondary 
    soft constraints or fail specific checks.

    :param title: The title of the filter as displayed in the admin interface.
    :type title: str
    :param parameter_name: The query parameter used in the admin interface to select the filter option.
    :type parameter_name: str
    """
    title = _("secondary soft constraints")
    parameter_name = "soft_secondary_constraints"

    def lookups(self, request, model_admin):
        """Define the filter options for the secondary soft constraints.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param model_admin: The model admin class where this filter is applied.
        :type model_admin: ModelAdmin
        :return: A tuple of filter options.
        :rtype: tuple
        """
        return (
            ('all_pass', _('All Pass')),
            ('fail_all_demonstrator', _('Fail - Missing Demonstrators')),
            ('fail_required_skill', _('Fail - Demonstrator missing competence at required level')),
        )
    
    def queryset(self, request, queryset):
        """Filter the queryset of allocations based on the selected secondary soft constraint option.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param queryset: The queryset of allocations to filter.
        :type queryset: QuerySet
        :return: A filtered queryset based on the selected secondary soft constraint option.
        :rtype: QuerySet
        """
        if self.value() == 'all_pass':
            valid_allocations = ConstrantFilterQuery.filter_allocation_by_secondary_soft_constraints(queryset)
            return queryset.filter(id__in=valid_allocations)
        elif self.value() == 'fail_all_demonstrator':
            valid_allocations = [
                allocation.id for allocation in queryset
                if not cm.SecondaryConstraintManager.session_has_all_demonstrators(allocation)
            ]
            return queryset.filter(id__in=valid_allocations)
        elif self.value() == 'fail_required_skill':
            valid_allocations = [
                allocation.id for allocation in queryset
                if not cm.SecondaryConstraintManager.demonstrator_has_skill_or_higher(allocation)
            ]
            return queryset.filter(id__in=valid_allocations)
        return queryset