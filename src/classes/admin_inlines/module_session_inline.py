from django.contrib import admin
from classes.models import SessionSchedule, ModuleSession
from django.urls import reverse
from django.utils.html import format_html

class SessionScheduleInline(admin.TabularInline):
    """The `SessionScheduleInline` class is a Django admin inline model that allows `SessionSchedule` instances to be 
    displayed and edited within the context of a related `ModuleSession` model. This inline uses a tabular layout 
    to display the `SessionSchedule` objects.

    :param model: The model associated with this inline, in this case, `SessionSchedule`.
    :type model: Model
    :param extra: The number of empty forms to display for creating new instances. Default is 0.
    :type extra: int
    :param fields: A list of fields to display in the inline.
    :type fields: list
    :param readonly_fields: A list of fields that are displayed as read-only.
    :type readonly_fields: list
    """
    model =  SessionSchedule
    extra = 0
    fields = ['timeslot', 'get_class_type']
    readonly_fields = ['get_class_type']
    
    def get_class_type(self, obj):
        """Return the class type associated with the session schedule.

        :param obj: The `SessionSchedule` instance.
        :type obj: SessionSchedule
        :return: The session type of the associated class session.
        :rtype: str
        """
        return obj.class_session.session_type
    get_class_type.short_description = "Class Type"
    
class ModuleSessionInline(admin.TabularInline):
    """The `ModuleSessionInline` class is a Django admin inline model that allows `ModuleSession` instances to be 
    displayed and edited within the context of a related model, typically a `Module` or similar entity. This inline 
    uses a tabular layout to display the `ModuleSession` objects.

    :param model: The model associated with this inline, in this case, `ModuleSession`.
    :type model: Model
    :param extra: The number of empty forms to display for creating new instances. Default is 0.
    :type extra: int
    :param fields: A list of fields to display in the inline.
    :type fields: list
    :param readonly_fields: A list of fields that are displayed as read-only.
    :type readonly_fields: list
    :param inlines: A list of inline classes to be nested within this inline.
    :type inlines: list
    """
    model = ModuleSession
    extra = 0
    fields = ["session_type", "required_demonstrator", "view_session_details"]
    readonly_fields = ["view_session_details"]
    inlines = [SessionScheduleInline]
    
    def view_session_details(self, obj):
        """Provide a link to view detailed session information in the admin interface.

        :param obj: The `ModuleSession` instance.
        :type obj: ModuleSession
        :return: An HTML link to the module session change page.
        :rtype: str
        """
        url = reverse("admin:classes_modulesession_change", args=[obj.id])
        return format_html('<a href="{}">View Details</a>', url)
    view_session_details.short_description = "Session Details"