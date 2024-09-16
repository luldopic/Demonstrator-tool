from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User, UserAvailability
from classes.models import Competency, Skill, ModuleSession, RequirementSkill

class UserForm(forms.ModelForm):
    """The `UserForm` class provides a form for updating basic user details, such as first name, last name, and email. 
    It is tied to the `User` model.

    :param Meta.model: The model associated with this form, in this case, `User`.
    :type Meta.model: Model
    :param Meta.fields: A list of fields that will be included in the form.
    :type Meta.fields: list
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class AvailabilityForm(forms.ModelForm):
    """The `AvailabilityForm` class provides a form for updating user availability. It is tied to the `UserAvailability` model 
    and includes fields for selecting a timeslot and indicating whether the user is available.

    :param Meta.model: The model associated with this form, in this case, `UserAvailability`.
    :type Meta.model: Model
    :param Meta.fields: A list of fields that will be included in the form.
    :type Meta.fields: list
    """
    class Meta:
        model = UserAvailability
        fields = ['timeslot', 'is_available']

class CompetencyForm(forms.ModelForm):
    """The `CompetencyForm` class provides a form for managing a user's competency in a specific skill. 
    It is tied to the `Competency` model and includes a field for selecting the relevant skill.

    :param Meta.model: The model associated with this form, in this case, `Competency`.
    :type Meta.model: Model
    :param Meta.fields: A list of fields that will be included in the form.
    :type Meta.fields: list
    """
    class Meta:
        model = Competency
        fields = ['skill']
        
class UserRegistrationForm(UserCreationForm):
    """The `UserRegistrationForm` class extends Django's `UserCreationForm` to include additional fields for registering a new user. 
    It includes fields for first name, last name, and email, in addition to the standard username and password fields.

    :param first_name: A character field for the user's first name, required for registration.
    :type first_name: CharField
    :param last_name: A character field for the user's last name, required for registration.
    :type last_name: CharField
    :param email: An email field for the user's email address, required for registration.
    :type email: EmailField
    :param Meta.model: The model associated with this form, in this case, `User`.
    :type Meta.model: Model
    :param Meta.fields: A list of fields that will be included in the form.
    :type Meta.fields: list
    """
    first_name = forms.CharField(max_length=30, required=True, help_text='Required')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required')
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class SessionUpdateForm(forms.Form):
    """The `SessionUpdateForm` class provides a form for updating the details of a module session. 
    It includes fields for specifying the number of required demonstrators and selecting relevant skills.

    :param session_id: A hidden integer field representing the ID of the session to be updated.
    :type session_id: IntegerField (HiddenInput)
    :param required_demonstrators: An integer field for specifying the number of required demonstrators, with a minimum value of 0.
    :type required_demonstrators: IntegerField
    :param skills: A multiple choice field allowing the selection of relevant skills for the session, displayed as checkboxes.
    :type skills: ModelMultipleChoiceField
    """
    session_id = forms.IntegerField(widget=forms.HiddenInput())
    required_demonstrators = forms.IntegerField(label='Number of Demonstrators', min_value=0)
    skills = forms.ModelMultipleChoiceField(queryset=Skill.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
class SkillCreationForm(forms.Form):
    """The `SkillCreationForm` class provides a form for creating a new skill. 
    It includes a single field for entering the name of the skill.

    :param name: A character field for the name of the new skill, with a maximum length of 100 characters.
    :type name: CharField
    """
    name = forms.CharField(label='New Skill', max_length=100)
    
class ProfileCompetencyForm(forms.Form):
    """The `ProfileCompetencyForm` class provides a form for selecting multiple skills to associate with a user's profile. 
    It includes a multiple choice field allowing the selection of skills, displayed as checkboxes.

    :param skills: A multiple choice field allowing the selection of relevant skills, displayed as checkboxes.
    :type skills: ModelMultipleChoiceField
    """
    skills = forms.ModelMultipleChoiceField(queryset=Skill.objects.all(), widget=forms.CheckboxSelectMultiple)