from django.contrib import admin
from allocations.models import Allocation, AllocationDomain
from allocations.utils.allocation_manager import AllocationManager
from allocations.utils.constraint_filter import HardConstraintFilter, SoftPrimaryConstraintFilter, SoftSecondaryConstraintFilter
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

# Register your models here.
class AllocationAdmin(admin.ModelAdmin):
    """The `AllocationAdmin` class customizes the Django admin interface for the `Allocation` model. It provides 
    functionalities such as filtering allocations by constraints, displaying session details, and managing 
    the approval status of allocations.

    This class defines custom actions for ensuring correct approval statuses, populating solution domains, 
    automatically assigning demonstrators, and resetting allocations.

    :param list_display: A list of fields or methods to display in the admin list view.
    :type list_display: list
    :param list_filter: A list of filters available in the admin list view.
    :type list_filter: list
    :param actions: A list of custom actions available in the admin interface.
    :type actions: list
    """
    list_display = ["get_session_details", "get_demonstrator_name", "approved"]
    list_filter = ["approved", HardConstraintFilter, SoftPrimaryConstraintFilter, SoftSecondaryConstraintFilter]
    actions = ["ensure_correct_approved_status", "populate_solution_domain", "assign_demonstrator", "reset_allocation"]
    
    
    def get_session_details(self, obj):
        """Display session details including the class code and session type.

        :param obj: The `Allocation` instance.
        :type obj: Allocation
        :return: A string combining the class code and session type.
        :rtype: str
        """
        class_code = obj.class_session.class_code.class_code
        class_type = obj.class_session.session_type
        return str(class_code)+" "+str(class_type)
    get_session_details.short_description = "Session Details"
    
    def get_demonstrator_name(self, obj):
        """Display the name of the demonstrator assigned to the allocation.

        :param obj: The `Allocation` instance.
        :type obj: Allocation
        :return: The full name of the demonstrator or '-' if none is assigned.
        :rtype: str
        """
        if obj.demonstrator == None:
            return "-"
        first_name = obj.demonstrator.user.first_name
        last_name = obj.demonstrator.user.last_name
        return str(first_name)+" "+str(last_name)
    get_demonstrator_name.short_description = "Demonstrator"
    
    def ensure_correct_approved_status(self, request, queryset):
        """Ensure that allocations are not approved if no demonstrator is assigned.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param queryset: A queryset of selected allocations.
        :type queryset: QuerySet
        """
        for allocation in queryset:
            allocation.ensure_not_approved_if_no_demonstrator()
        self.message_user(request, "Checked and adjusted allocation status for selected allocations.")
    ensure_correct_approved_status.short_description = "Ensure Correct Allocation Status"
    
    def view_module_session(self, obj):
        """Provide a link to view the related module session in the admin interface.

        :param obj: The `Allocation` instance.
        :type obj: Allocation
        :return: An HTML link to the module session change page.
        :rtype: str
        """
        url = reverse("admin:classes_modulesession_change", args=[obj.class_session.id])
        return format_html('<a href="{}">View Module Session</a>', url)
    view_module_session.short_description = "Module Session"
    
    def changelist_view(self, request, extra_context=None):
        """Customize the changelist view to filter allocations by class session ID if specified in the query parameters.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param extra_context: Additional context for the changelist view.
        :type extra_context: dict, optional
        :return: The modified changelist view.
        :rtype: HttpResponse
        """
        class_session_ids = request.GET.get('class_session__id__in')
        if class_session_ids:
            class_session_ids = class_session_ids.split(',')
            self.queryset = self.get_queryset(request).filter(class_session__id__in=class_session_ids)
        return super().changelist_view(request, extra_context=extra_context)
    
    def populate_solution_domain(self, request, queryset):
        """Populate the solution domain for selected allocations, determining viable demonstrators.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param queryset: A queryset of selected allocations.
        :type queryset: QuerySet
        """
        for allocation in queryset:
            AllocationManager.get_solution_domain(allocation)
        self.message_user(request, "Populated solution domain for selected allocations.")
    populate_solution_domain.short_description = "Get viable demonstrators"
    
    def assign_demonstrator(self, request, queryset):
        """Automatically assign demonstrators to selected allocations.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param queryset: A queryset of selected allocations.
        :type queryset: QuerySet
        """
        res = AllocationManager.assign_demonstrators(queryset)
        if res:
            self.message_user(request,"Successfully assigned demonstrators")
        else:
            self.message_user(request, "Failed assigning demonstrators")
    assign_demonstrator.short_description = "Automatically assign demonstrators"
    
    def reset_allocation(self, request, queryset):
        """Reset selected allocations by unassigning the demonstrators.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param queryset: A queryset of selected allocations.
        :type queryset: QuerySet
        """
        for allocation in queryset:
            allocation.demonstrator = None
            allocation.save()
        self.message_user(request, "Demonstrator unallocated")
    reset_allocation.short_description = "Unallocate demonstrators"


class AllocationDomainAdmin(admin.ModelAdmin):
    """The `AllocationDomainAdmin` class customizes the Django admin interface for the `AllocationDomain` model. 
    It provides functionalities to display details about the session and the number of viable demonstrators 
    for each constraint level.

    :param list_display: A list of fields or methods to display in the admin list view.
    :type list_display: list
    """
    list_display = ["get_session_details",
                    "get_viable_hard_constraint_number",
                    "get_viable_primary_constraint_number",
                    "get_viable_secondary_constraint_number",
                    "get_viable_tertiary_constraint_number",
                    "view_module_session"]
    
    def get_session_details(self, obj):
        """Display session details including the class code and session type.

        :param obj: The `AllocationDomain` instance.
        :type obj: AllocationDomain
        :return: A string combining the class code and session type.
        :rtype: str
        """
        class_code = obj.allocation.class_session.class_code.class_code
        class_type = obj.allocation.class_session.session_type
        return str(class_code)+" "+str(class_type)
    get_session_details.short_description = "Session Details"
    
    def get_viable_hard_constraint_number(self, obj):
        """Display the number of demonstrators that meet hard constraints for the session.

        :param obj: The `AllocationDomain` instance.
        :type obj: AllocationDomain
        :return: The number of viable demonstrators that meet hard constraints.
        :rtype: int
        """
        return obj.hard_constraint_demonstrators.count()
    get_viable_hard_constraint_number.short_description = "N viable with hard constraints"
    
    def get_viable_primary_constraint_number(self, obj):
        """Display the number of demonstrators that meet primary soft constraints for the session.

        :param obj: The `AllocationDomain` instance.
        :type obj: AllocationDomain
        :return: The number of viable demonstrators that meet primary soft constraints.
        :rtype: int
        """
        return obj.primary_soft_constraint_demonstrators.count()
    get_viable_primary_constraint_number.short_description = "N viable with primary soft constraints"
    
    def get_viable_secondary_constraint_number(self, obj):
        """Display the number of demonstrators that meet secondary soft constraints for the session.

        :param obj: The `AllocationDomain` instance.
        :type obj: AllocationDomain
        :return: The number of viable demonstrators that meet secondary soft constraints.
        :rtype: int
        """
        return obj.secondary_soft_constraint_demonstrators.count()
    get_viable_secondary_constraint_number.short_description = "N viable with secondary soft constraints"
    
    def get_viable_tertiary_constraint_number(self, obj):
        """Display the number of demonstrators that meet tertiary constraints for the session.

        :param obj: The `AllocationDomain` instance.
        :type obj: AllocationDomain
        :return: The number of viable demonstrators that meet tertiary constraints.
        :rtype: int
        """
        return obj.tertiary_soft_constraint_demonstrators.count()
    get_viable_tertiary_constraint_number.short_description = "N viable with tertiary constraints"
    
    def view_module_session(self, obj):
        """Provide a link to view the related module session in the admin interface.

        :param obj: The `AllocationDomain` instance.
        :type obj: AllocationDomain
        :return: An HTML link to the module session change page.
        :rtype: str
        """
        url = reverse("admin:classes_modulesession_change", args=[obj.allocation.class_session.id])
        return format_html('<a href="{}">View Module Session</a>', url)
    view_module_session.short_description = "Module Session"

admin.site.register(Allocation, AllocationAdmin)
admin.site.register(AllocationDomain, AllocationDomainAdmin)

