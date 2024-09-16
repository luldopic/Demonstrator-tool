from django.contrib import admin
from users.models import User, Demonstrator, Lecturer
from classes.models import UserAvailability
from timetable.models import Timeslot
from classes.admin_inlines.skill_inline import CompetencyInline
from classes.admin_inlines.module_lecturer_inline import ModuleInline
from django.urls import reverse
from django.utils.html import format_html

class UserAdmin(admin.ModelAdmin):
    """The `UserAdmin` class customizes the Django admin interface for the `User` model. It includes search fields, 
    list displays, list filters, and actions for managing users.

    :param search_fields: Fields to include in the search functionality.
    :type search_fields: list
    :param list_display: Fields to display in the list view of the admin interface.
    :type list_display: list
    :param list_filter: Filters to apply to the list view of the admin interface.
    :type list_filter: list
    :param actions: Custom actions available in the admin interface.
    :type actions: list
    """
    search_fields = ["first_name", "last_name","username"]
    list_display = ["username","first_name", "last_name"]
    list_filter = ["is_lecturer", "is_demonstrator"]
    actions = ["create_user_availability"]
    
    def create_user_availability(self, request, queryset):
        """Create or update the availability records for selected users across all available timeslots.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param queryset: The queryset of selected users.
        :type queryset: QuerySet
        :return: None
        """
        timeslots = Timeslot.objects.all()
        count = 0
        for user in queryset:
            for slot in timeslots:
                if not UserAvailability.objects.filter(user=user, timeslot=slot).exists():
                    UserAvailability.objects.create(user=user, timeslot=slot)
            count += 1
        self.message_user(request, f'User availability created/updated for {count} users.')

    create_user_availability.short_description = "Create/Update User Availability"

class RoleAdminMixin:
    """The `RoleAdminMixin` class provides utility methods and permissions for models related to user roles, 
    such as `Lecturer` and `Demonstrator`. These methods include retrieving user names and viewing user details.
    """
    def get_first_name(self, obj):
        """Return the first name of the user associated with the role.

        :param obj: The role instance (e.g., `Lecturer` or `Demonstrator`).
        :type obj: Model instance
        :return: The user's first name.
        :rtype: str
        """
        return obj.user.first_name
    get_first_name.short_description = "First Name"
    
    def get_last_name(self, obj):
        """Return the last name of the user associated with the role.

        :param obj: The role instance (e.g., `Lecturer` or `Demonstrator`).
        :type obj: Model instance
        :return: The user's last name.
        :rtype: str
        """
        return obj.user.last_name
    get_last_name.short_description = "Last Name"
    
    def view_user(self, obj):
        """Provide a link to view the user details in the admin interface.

        :param obj: The role instance (e.g., `Lecturer` or `Demonstrator`).
        :type obj: Model instance
        :return: A formatted HTML link to the user's details page.
        :rtype: str
        """
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">View User</a>', url)
    view_user.short_description = "User Details"
    
    def has_delete_permission(self, request, obj=None):
        """Return `True` to allow delete permissions for the role.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param obj: The role instance (optional).
        :type obj: Model instance, optional
        :return: `True` to allow delete permissions.
        :rtype: bool
        """
        return True

    def has_change_permission(self, request, obj=None):
        """Return `True` to allow change permissions for the role.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param obj: The role instance (optional).
        :type obj: Model instance, optional
        :return: `True` to allow change permissions.
        :rtype: bool
        """
        return True

    def has_view_permission(self, request, obj=None):
        """Return `True` to allow view permissions for the role.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param obj: The role instance (optional).
        :type obj: Model instance, optional
        :return: `True` to allow view permissions.
        :rtype: bool
        """
        return True

class LecturerAdmin(admin.ModelAdmin, RoleAdminMixin):
    """The `LecturerAdmin` class customizes the Django admin interface for the `Lecturer` model. It includes inline models,
    search fields, and list displays for managing lecturers.

    :param inlines: Inline models to include in the form.
    :type inlines: list
    :param search_fields: Fields to include in the search functionality.
    :type search_fields: list
    :param list_display: Fields to display in the list view of the admin interface.
    :type list_display: list
    """
    inlines = [ModuleInline]
    search_fields = ["user__first_name", "user__last_name","department"]
    list_display = ["get_first_name", "get_last_name", "department", "view_user"]
    
class DemonstratorAdmin(admin.ModelAdmin, RoleAdminMixin):
    """The `DemonstratorAdmin` class customizes the Django admin interface for the `Demonstrator` model. It includes inline models,
    search fields, and list displays for managing demonstrators.

    :param inlines: Inline models to include in the form.
    :type inlines: list
    :param search_fields: Fields to include in the search functionality.
    :type search_fields: list
    :param list_display: Fields to display in the list view of the admin interface.
    :type list_display: list
    """
    inlines = [CompetencyInline]
    search_fields = ["user__first_name", "user__last_name", "competency__skill__name"]
    list_display = ["get_first_name", "get_last_name", "view_user"]


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Demonstrator, DemonstratorAdmin)
admin.site.register(Lecturer, LecturerAdmin)