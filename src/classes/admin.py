from typing import Any
from django.contrib import admin
from django.db.models import Sum, Q
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from classes.models import Module, ModuleSession, Skill, RequirementSkill, SessionSchedule, Competency
from classes.admin_inlines.skill_inline import RequirementInline
from classes.admin_inlines.module_session_inline import ModuleSessionInline
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode



class SkillAdmin(admin.ModelAdmin):
    """The `SkillAdmin` class customizes the Django admin interface for the `Skill` model. It includes search fields, 
    list displays, and fields for managing skills.

    :param search_fields: Fields to include in the search functionality.
    :type search_fields: list
    :param list_display: Fields to display in the list view of the admin interface.
    :type list_display: list
    :param fields: Fields to include in the form for adding/editing skills.
    :type fields: list
    """
    search_fields = ["name"]
    list_display = ["name", "level"]
    fields = ["name"]
    
    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        """Customize the save behavior to ensure a new skill is created or an existing one is updated.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param obj: The skill instance being saved.
        :type obj: Skill
        :param form: The form used to input the skill data.
        :type form: ModelForm
        :param change: Boolean indicating whether this is an update to an existing object.
        :type change: bool
        :return: None
        """
        if not change:
            Skill.objects.create(name=obj.name)
        else:
            super().save_model(request, obj, form, change)

class ModuleAdmin(admin.ModelAdmin):
    """The `ModuleAdmin` class customizes the Django admin interface for the `Module` model. It includes list displays, 
    fields, inlines, and custom actions for managing modules.

    :param list_display: Fields to display in the list view of the admin interface.
    :type list_display: list
    :param fields: Fields to include in the form for adding/editing modules.
    :type fields: list
    :param inlines: Inline models to include in the form.
    :type inlines: list
    """
    list_display = ["class_code", 'name', "formatted_lecturer_name", "formatted_semester", "num_sessions", "num_schedules", "view_module_sessions"]
    fields = ["class_code", "name", "lecturer", "semester"]
    inlines = [ModuleSessionInline]
    
    def view_module_sessions(self, obj):
        """Provide a link to view all sessions associated with the module.

        :param obj: The module instance.
        :type obj: Module
        :return: A formatted HTML link to the sessions list.
        :rtype: str
        """
        url = (
            reverse("admin:classes_modulesession_changelist")
            + "?"
            + urlencode({"class_code__class_code__exact": obj.class_code})
        )
        return format_html('<a href="{}">View Sessions</a>', url)
    view_module_sessions.short_description = "Module Sessions"
    
    def num_sessions(self, obj):
        """Return the number of session types for the module.

        :param obj: The module instance.
        :type obj: Module
        :return: The count of session types.
        :rtype: int
        """
        return obj.count_sessions()[0]
    num_sessions.short_description = "Number of Session Types"
    
    def num_schedules(self, obj):
        """Return the number of timeslots used by the module's sessions.

        :param obj: The module instance.
        :type obj: Module
        :return: The count of timeslots used.
        :rtype: int
        """
        return obj.count_sessions()[1]
    num_schedules.short_description = "Timeslot used"


class ModuleSessionMixin:
    """The `ModuleSessionMixin` class provides utility methods and actions for the `ModuleSessionAdmin` class, 
    including methods for retrieving class codes, ensuring correct allocation, and viewing module sessions.
    """
    def get_class_code(self, obj):
        """Return the class code associated with the session.

        :param obj: The module session instance.
        :type obj: ModuleSession
        :return: The class code.
        :rtype: str
        """
        return obj.class_code.class_code
    get_class_code.short_description = "Class Code"
    
    def total_required_demonstrators(self, request, queryset):
        """Calculate and display the total number of required demonstrators for the selected sessions.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param queryset: The queryset of selected sessions.
        :type queryset: QuerySet
        :return: None
        """
        total = queryset.aggregate(total=Sum("required_demonstrator"))["total"]
        self.message_user(request, f"Total required demonstrator: {total}")
    total_required_demonstrators.short_description = "Total Required Demonstator"
    
    def ensure_correct_allocation(self, request, queryset):
        """Ensure that the allocations for the selected sessions are correct.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param queryset: The queryset of selected sessions.
        :type queryset: QuerySet
        :return: None
        """
        for module_session in queryset:
            module_session.ensure_correct_allocation()
        self.message_user(request, "Checked and adjusted allocations for selected module sessions.")
    ensure_correct_allocation.short_description = "Ensure Correct Allocation"
    
    def view_module_session(self, obj):
        """Provide a link to view the module session details.

        :param obj: The module session instance.
        :type obj: ModuleSession
        :return: A formatted HTML link to the session details page.
        :rtype: str
        """
        url = reverse("admin:classes_modulesession_change", args=[obj.class_session.id])
        return format_html('<a href="{}">View Module Session</a>', url)
    view_module_session.short_description = "Module Session"
    
    def get_queryset(self, request):
        """Filter the queryset based on the class code if provided.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :return: The filtered queryset.
        :rtype: QuerySet
        """
        queryset = super().get_queryset(request)
        class_code = request.GET.get('class_code__id__exact')
        if class_code:
            queryset = queryset.filter(class_code__id=class_code)
        return queryset

    def changelist_view(self, request, extra_context=None):
        """Customize the changelist view to filter sessions by class code if provided.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param extra_context: Additional context for the changelist view.
        :type extra_context: dict
        :return: The modified changelist view.
        :rtype: HttpResponse
        """
        class_code = request.GET.get('class_code__id__exact')
        if class_code:
            request.META['QUERY_STRING'] = urlencode({'class_code__id__exact': class_code})
        return super().changelist_view(request, extra_context=extra_context)
    
    def view_module(self, obj):
        """Provide a link to view the module details.

        :param obj: The module session instance.
        :type obj: ModuleSession
        :return: A formatted HTML link to the module details page.
        :rtype: str
        """
        url = reverse("admin:classes_module_change", args=[obj.class_code.class_code])
        return format_html('<a href="{}">View Module</a>', url)
    view_module.short_description = "Module"
    
    def get_search_results(self, request: HttpRequest, queryset: QuerySet, search_term: str) -> tuple[QuerySet, bool]:
        """Customize the search results to include class codes that match the search term.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param queryset: The queryset of sessions to search.
        :type queryset: QuerySet
        :param search_term: The search term entered by the user.
        :type search_term: str
        :return: The filtered queryset and a boolean indicating whether distinct results are required.
        :rtype: tuple[QuerySet, bool]
        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            search_terms = search_term.split()
            queries = Q()
            for term in search_terms:
                queries |= Q(class_code__class_code__icontains=term)
            queryset = queryset.filter(queries)
        return queryset, use_distinct
    
    def view_allocations(self, request, queryset):
        """Provide a link to view allocations for the selected sessions.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param queryset: The queryset of selected sessions.
        :type queryset: QuerySet
        :return: A redirect response to the allocations list page.
        :rtype: HttpResponseRedirect
        """
        session_ids = queryset.values_list('id', flat=True)
        query_params = urlencode({'class_session__id__in': ','.join(map(str, session_ids))})
        url = f"{reverse('admin:allocations_allocation_changelist')}?{query_params}"
        return HttpResponseRedirect(url)
    view_allocations.short_description = "View Allocations of Selected Sessions"


class ModuleSessionAdmin(admin.ModelAdmin, ModuleSessionMixin):
    """The `ModuleSessionAdmin` class customizes the Django admin interface for the `ModuleSession` model. It includes list displays, 
    filters, inlines, actions, and search fields for managing module sessions.

    :param inlines: Inline models to include in the form.
    :type inlines: list
    :param list_display: Fields to display in the list view of the admin interface.
    :type list_display: list
    :param list_filter: Filters to apply to the list view of the admin interface.
    :type list_filter: list
    :param actions: Custom actions available in the admin interface.
    :type actions: list
    :param search_fields: Fields to include in the search functionality.
    :type search_fields: list
    """
    inlines = [RequirementInline]
    list_display = ["get_class_code", "session_type" ,"required_demonstrator", "view_module"]
    list_filter = ["session_type"]
    actions = ["total_required_demonstrators", "ensure_correct_allocation", "view_allocations"]
    search_fields = ["class_code__class_code"]
    


class RequirementsMixin:
    """The `RequirementsMixin` class provides utility methods for the `RequirementsAdmin` class, including methods 
    for retrieving class codes, displaying skill levels, and viewing module sessions.
    """
    def get_class_code(self, obj):
        """Return the class code associated with the requirement.

        :param obj: The requirement skill instance.
        :type obj: RequirementSkill
        :return: The class code.
        :rtype: str
        """
        return obj.class_session.class_code.class_code
    get_class_code.short_description = "Class Code"
    
    def get_skill_display(self, obj):
        """Return a formatted display of the skill level and name.

        :param obj: The requirement skill instance.
        :type obj: RequirementSkill
        :return: The formatted skill display.
        :rtype: str
        """
        return f"{obj.skill.get_level_display()} {obj.skill.name}"
    get_skill_display.short_description = "Skill"
    
    def view_module_session(self, obj):
        """Provide a link to view the module session details.

        :param obj: The requirement skill instance.
        :type obj: RequirementSkill
        :return: A formatted HTML link to the session details page.
        :rtype: str
        """
        url = reverse("admin:classes_modulesession_change", args=[obj.class_session.id])
        return format_html('<a href="{}">View Module Session</a>', url)
    view_module_session.short_description = "Module Session"


class RequirementsAdmin(admin.ModelAdmin, RequirementsMixin):
    """The `RequirementsAdmin` class customizes the Django admin interface for the `RequirementSkill` model. 
    It includes list displays, search fields, and fields for managing requirement skills.

    :param list_display: Fields to display in the list view of the admin interface.
    :type list_display: list
    :param search_fields: Fields to include in the search functionality.
    :type search_fields: list
    :param fields: Fields to include in the form for adding/editing requirement skills.
    :type fields: list
    """
    list_display = ["get_class_code", "get_skill_display"]
    search_fields = ["class_session__class_code__class_code","skill__name"]
    fields = ["class_session", "skill"]    

    
class CompetencyMixin:
    """The `CompetencyMixin` class provides utility methods for the `CompetencyAdmin` class, including methods 
    for retrieving demonstrator names and displaying skill levels.
    """
    def get_demonstrator_name(self, obj):
        """Return the name of the demonstrator associated with the competency.

        :param obj: The competency instance.
        :type obj: Competency
        :return: The demonstrator's full name.
        :rtype: str
        """
        return f"{obj.demonstrator.user.first_name} {obj.demonstrator.user.last_name}"
    get_demonstrator_name.short_description = "Demonstrator"
    
    def get_skill_display(self, obj):
        """Return a formatted display of the skill level and name.

        :param obj: The competency instance.
        :type obj: Competency
        :return: The formatted skill display.
        :rtype: str
        """
        return f"{obj.skill.get_level_display()} {obj.skill.name}"
    get_skill_display.short_description = "Skill"
    
    
class CompetencyAdmin(admin.ModelAdmin, CompetencyMixin):
    """The `CompetencyAdmin` class customizes the Django admin interface for the `Competency` model. 
    It includes list displays and search fields for managing competencies.

    :param list_display: Fields to display in the list view of the admin interface.
    :type list_display: list
    :param search_fields: Fields to include in the search functionality.
    :type search_fields: list
    """
    list_display = ["get_demonstrator_name", "get_skill_display"]
    search_fields = ["skill__name"]
    
    
class SessionScheduleAdmin(admin.ModelAdmin):
    """The `SessionScheduleAdmin` class customizes the Django admin interface for the `SessionSchedule` model. 
    It includes list displays and search fields for managing session schedules.

    :param list_display: Fields to display in the list view of the admin interface.
    :type list_display: list
    :param search_fields: Fields to include in the search functionality.
    :type search_fields: list
    """
    list_display = ["get_class_code", "get_class_type", "timeslot"]
    search_fields = ["class_session__class_code__class_code"]
    
    
    
    def get_class_code(self, obj):
        """Return the class code associated with the session schedule.

        :param obj: The session schedule instance.
        :type obj: SessionSchedule
        :return: The class code.
        :rtype: str
        """
        return obj.class_session.class_code.class_code
    get_class_code.short_description = "Class Code"
    
    def get_class_type(self, obj):
        """Return the class type associated with the session schedule.

        :param obj: The session schedule instance.
        :type obj: SessionSchedule
        :return: The class type.
        :rtype: str
        """
        return obj.class_session.session_type
    get_class_type.short_description = "Class Type"
    

# Register your models here.
admin.site.register(Module,ModuleAdmin)
admin.site.register(ModuleSession, ModuleSessionAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(RequirementSkill, RequirementsAdmin)
admin.site.register(SessionSchedule, SessionScheduleAdmin)
admin.site.register(Competency, CompetencyAdmin)