from classes.models import Module
from users.models import Lecturer
from timetable.models import Semester
from django.contrib import admin
from django import forms

class ModuleInlineForm(forms.ModelForm):
    """The `ModuleInlineForm` class represents a custom form used in the Django admin interface for managing `Module` instances. 
    This form allows the user to input and edit fields related to the `Module` model, such as `class_code` and `name`.

    :param class_code: A character field for the class code, limited to a maximum of 30 characters.
    :type class_code: CharField
    :param name: A character field for the module name, limited to a maximum of 100 characters.
    :type name: CharField
    """
    class_code = forms.CharField(max_length=30)
    name = forms.CharField(max_length=100)

    
    class Meta:
        """Metadata options for the `ModuleInlineForm` class.

        :param model: The model that this form is associated with, in this case, `Module`.
        :type model: Model
        :param fields: A list of fields that will be included in the form.
        :type fields: list
        """
        model = Module
        fields = ["lecturer", "class_code", "name"]
        
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['skill_name'].initial = self.instance.skill.name
            self.fields['skill_level'].initial = self.instance.skill.level
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        skill_name = self.cleaned_data['skill_name']
        skill_level = self.cleaned_data['skill_level']

        # Update or create the related skill
        skill_qs = Skill.objects.filter(name=skill_name, level= skill_level)
        if skill_qs.exists:
            skill = skill_qs.first()
        else:
            skill, created = Skill.objects.create(name=skill_name, level = skill_level)

        instance.skill = skill

        if commit:
            instance.save()
        return instance
    """

class ModuleInline(admin.TabularInline):
    """The `ModuleInline` class is a Django admin inline model that allows the `Module` instances to be displayed 
    and edited within the context of a related model, typically a `Lecturer` or similar entity. This inline uses 
    a tabular layout to display the `Module` objects.

    :param model: The model associated with this inline, in this case, `Module`.
    :type model: Model
    :param extra: The number of empty forms to display for creating new instances. Default is 0.
    :type extra: int
    """
    model = Module
    # form = ModuleInlineForm
    extra = 0