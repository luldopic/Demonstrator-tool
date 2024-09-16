from typing import Any
from django.contrib import admin
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import HttpRequest
from timetable.models import Timeslot, Semester
from classes.models import SessionSchedule
from users.models import UserAvailability


# Register your models here.

class SemesterAdmin(admin.ModelAdmin):
    """The `SemesterAdmin` class customizes the Django admin interface for the `Semester` model. It includes search fields 
    and list displays to manage semesters.

    :param search_fields: Fields to include in the search functionality.
    :type search_fields: list
    :param list_display: Fields to display in the list view of the admin interface.
    :type list_display: list
    """
    search_fields = ["year", "semester"]
    list_display = ["year", "semester"]
    
class TimeslotAdmin(admin.ModelAdmin):
    """The `TimeslotAdmin` class customizes the Django admin interface for the `Timeslot` model. It includes list displays 
    and ordering to manage timeslots.

    :param list_display: Fields to display in the list view of the admin interface.
    :type list_display: list
    :param ordering: Fields by which to order the list view.
    :type ordering: list
    """
    list_display = ["day", "start_time", "end_time"]
    ordering = ["day", "start_time"]
    
class TimetableMixin:
    """The `TimetableMixin` class provides utility methods for displaying information about timeslots in related models."""
    def get_timeslot(self, obj):
        """Return a formatted string representing the timeslot associated with the object.

        :param obj: The instance of the model that contains a timeslot.
        :type obj: Model instance
        :return: A formatted string of the day and time range.
        :rtype: str
        """
        return f"{obj.timeslot.get_day_display()} {obj.timeslot.start_time}-{obj.timeslot.end_time}"
    get_timeslot.short_description = "Timeslot"
    
class SessionScheduleMixin(TimetableMixin):
    """The `SessionScheduleMixin` class is a subclass of `TimetableMixin` that provides additional functionality 
    for models related to session schedules."""
    pass

class UserAvailabilityMixin(TimetableMixin):
    """The `UserAvailabilityMixin` class is a subclass of `TimetableMixin` that provides additional functionality 
    for models related to user availability."""
    def get_user_name(self, obj):
        """Return the full name of the user associated with the availability record.

        :param obj: The instance of the model that contains user availability.
        :type obj: Model instance
        :return: The user's full name.
        :rtype: str
        """
        return obj.user.username
    get_user_name.short_description = "Username"

class UserAvailabilityAdmin(admin.ModelAdmin, UserAvailabilityMixin):
    """The `UserAvailabilityAdmin` class customizes the Django admin interface for the `UserAvailability` model. 
    It includes list displays, search fields, and a custom search results method for managing user availability.

    :param list_display: Fields to display in the list view of the admin interface.
    :type list_display: list
    :param search_fields: Fields to include in the search functionality.
    :type search_fields: list
    """
    list_display = ["get_user_name","get_timeslot","is_available"]
    search_fields = ["user__first_name", "user__last_name","user__username"]
    
    def get_search_results(self, request: HttpRequest, queryset: QuerySet[Any], search_term: str) -> tuple[QuerySet[Any], bool]:
        """Customize the search results to include user names that match the search term.

        :param request: The current HTTP request object.
        :type request: HttpRequest
        :param queryset: The queryset of user availability records to search.
        :type queryset: QuerySet
        :param search_term: The search term entered by the user.
        :type search_term: str
        :return: The filtered queryset and a boolean indicating whether distinct results are required.
        :rtype: tuple[QuerySet[Any], bool]
        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            search_term = search_term.split()
            queries = Q()
            for term in search_term:
                queries |= Q(user__first_name__icontains=term) | Q(user__last_name__icontains=term)
            queryset = queryset.filter(queries)
        return queryset, use_distinct

admin.site.register(Timeslot, TimeslotAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(UserAvailability,UserAvailabilityAdmin)
