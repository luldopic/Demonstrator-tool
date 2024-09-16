from classes.models import Competency, Skill, RequirementSkill
from django.contrib import admin
from django import forms

class SkillInlineForm(forms.ModelForm):
    """The `SkillInlineForm` class represents a custom form used in the Django admin interface for managing `Skill` instances. 
    This form provides fields to select a skill name and level, and handles the creation or retrieval of the associated `Skill` object.

    :param skill_name: A model choice field allowing the selection of a distinct skill name.
    :type skill_name: ModelChoiceField
    :param skill_level: A choice field for selecting the skill level, initialized to 0.
    :type skill_level: ChoiceField
    """
    skill_name = forms.ModelChoiceField(
        queryset=Skill.objects.values_list('name', flat=True).distinct(),
        empty_label="Select Skill Name"
    )
    skill_level = forms.ChoiceField(choices=Skill.LEVEL_CHOICES, initial=0)
    
    def __init__(self, *args, **kwargs):
        """Initialize the form with pre-filled data if an instance exists.

        :param args: Additional positional arguments.
        :type args: list
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        """
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['skill_name'].initial = self.instance.skill.name
            self.fields['skill_level'].initial = self.instance.skill.level
    
    def save(self, commit=True):
        """Save the form data, creating or updating the related `Skill` instance as necessary.

        :param commit: Whether to commit the save operation immediately.
        :type commit: bool, optional
        :return: The saved form instance.
        :rtype: SkillInlineForm
        """
        instance = super().save(commit=False)
        skill_name = self.cleaned_data['skill_name']
        skill_level = self.cleaned_data['skill_level']

        skill_qs = Skill.objects.filter(name=skill_name, level= skill_level)
        if skill_qs.exists:
            skill = skill_qs.first()
        else:
            skill, created = Skill.objects.create(name=skill_name, level = skill_level)

        instance.skill = skill

        if commit:
            instance.save()
        return instance
    
class CompetencyInlineForm(SkillInlineForm):
    """The `CompetencyInlineForm` class is a subclass of `SkillInlineForm` customized for the `Competency` model.
    
    :param Meta.model: The model associated with this form, in this case, `Competency`.
    :type Meta.model: Model
    :param Meta.fields: A list of fields included in the form.
    :type Meta.fields: list
    """
    class Meta:
        model = Competency
        fields = ["demonstrator", "skill_name", "skill_level"]
    
class RequirementInlineForm(SkillInlineForm):
    """The `RequirementInlineForm` class is a subclass of `SkillInlineForm` customized for the `RequirementSkill` model.
    
    :param Meta.model: The model associated with this form, in this case, `RequirementSkill`.
    :type Meta.model: Model
    :param Meta.fields: A list of fields included in the form.
    :type Meta.fields: list
    """
    class Meta:
        model = RequirementSkill
        fields = ["class_session", "skill_name", "skill_level"]

class CompetencyInline(admin.TabularInline):
    """The `CompetencyInline` class is a Django admin inline model that allows `Competency` instances to be displayed 
    and edited within the context of a related model, typically a `Demonstrator` or similar entity. This inline uses 
    a tabular layout to display the `Competency` objects.

    :param model: The model associated with this inline, in this case, `Competency`.
    :type model: Model
    :param form: The custom form used for managing `Competency` instances in this inline.
    :type form: ModelForm
    :param extra: The number of empty forms to display for creating new instances. Default is 0.
    :type extra: int
    """
    model = Competency
    form = CompetencyInlineForm
    extra = 0

class RequirementInline(admin.TabularInline):
    """The `RequirementInline` class is a Django admin inline model that allows `RequirementSkill` instances to be displayed 
    and edited within the context of a related model, typically a `ModuleSession` or similar entity. This inline uses 
    a tabular layout to display the `RequirementSkill` objects.

    :param model: The model associated with this inline, in this case, `RequirementSkill`.
    :type model: Model
    :param form: The custom form used for managing `RequirementSkill` instances in this inline.
    :type form: ModelForm
    :param extra: The number of empty forms to display for creating new instances. Default is 0.
    :type extra: int
    """
    model = RequirementSkill
    form = RequirementInlineForm
    extra = 0 