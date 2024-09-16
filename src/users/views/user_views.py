from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from users.models import User, UserAvailability, Demonstrator
from classes.models import Competency, Module, ModuleSession, SessionSchedule, Skill
from allocations.models import Allocation
from users.forms import UserForm, AvailabilityForm, ProfileCompetencyForm, UserRegistrationForm, SessionUpdateForm, SkillCreationForm
from timetable.models import Timeslot
from django.forms import modelformset_factory
import logging

logger = logging.getLogger(__name__)


class UserLoginView(LoginView):
    """The `UserLoginView` class provides a custom login view for handling user authentication. 
    It extends Django's `LoginView` and customizes the template and error handling.

    :param template_name: The template used for rendering the login page.
    :type template_name: str
    """
    template_name = "login.html"
    
    def form_valid(self, form):
        """Handle successful login form validation.
        
        :param form: The form submitted by the user.
        :type form: Form
        :return: A response rendering the login page with an error message.
        :rtype: HttpResponse
        """
        print(form.errors)
        user = form.get_user()
        if user is not None:
            print(f"User found: {user.username}, Active: {user.is_active}")  # Debugging line
            if user.is_active:
                login(self.request, user)
                return redirect(self.get_success_url())
            else:
                messages.error(self.request, "This account is inactive.")
        else:
            messages.error(self.request, "No user found with these credentials.")
        return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle invalid login attempts by displaying an error message.

        :param form: The form submitted by the user.
        :type form: Form
        :return: A response rendering the login page with an error message.
        :rtype: HttpResponse
        """
        print(form.errors)
        messages.error(self.request, "Authentication failed. Please check your username and password.")
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self) -> str:
        """Define the URL to redirect to upon successful login.

        :return: The URL of the dashboard.
        :rtype: str
        """
        return reverse_lazy("dashboard")


def user_logout(request):
    """Log the user out and redirect to the login page.

    :param request: The current HTTP request object.
    :type request: HttpRequest
    :return: A redirect response to the login page.
    :rtype: HttpResponseRedirect
    """
    logout(request)
    return redirect('login')

def user_registration(request):
    """Handle user registration by processing the registration form and creating a new user.

    :param request: The current HTTP request object.
    :type request: HttpRequest
    :return: A response rendering the registration page or redirecting to the dashboard on success.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('dashboard')
        else:
            print(form.errors)
            messages.error(request, 'Unsuccessful registration. Invalid information.')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration.html', {'form': form})


def home(request):
    """Redirect authenticated users to the dashboard, or render the login page for unauthenticated users.

    :param request: The current HTTP request object.
    :type request: HttpRequest
    :return: A redirect to the dashboard or a response rendering the login page.
    :rtype: HttpResponse or HttpResponseRedirect
    """
    if request.user.is_authenticated:
        return redirect("dashboard")
    else:
        return render(request,"login.html")

@login_required
def dashboard(request):
    """Render the dashboard with user-specific links based on their roles.

    :param request: The current HTTP request object.
    :type request: HttpRequest
    :return: A response rendering the dashboard page.
    :rtype: HttpResponse
    """
    user: User = request.user
    context = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "lecturer": user.is_lecturer,
        "demonstrator": user.is_demonstrator,
        "my_classes_url": reverse_lazy("class_list") if user.is_lecturer else None,
        "my_allocations_url": reverse_lazy("my_allocations") if user.is_demonstrator else None,
        "my_timetable_url": reverse_lazy("view_timetable")
    }
    return render(request, "dashboard.html", context)

@login_required
def view_user_profile(request):
    """Allow users to view and edit their profile, including personal details, availability, and competencies.

    :param request: The current HTTP request object.
    :type request: HttpRequest
    :return: A response rendering the profile page with forms for editing user details, availability, and competencies.
    :rtype: HttpResponse
    """
    user = request.user
    is_demonstrator = Demonstrator.objects.filter(user=user).exists()
    competencies = []
    competency_form = None

    # Handle user details form
    user_form = UserForm(instance=user)
    if request.method == 'POST' and 'user_details_form' in request.POST:
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "User details updated successfully.")
            return redirect('view_user_profile')

    # Handle availability form
    days = [(0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"), (4, "Friday"), (5, "Saturday"), (6, "Sunday")]
    hours = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]

    availability = {day: {hour: 'X' for hour in hours} for day, _ in days}
    availability_qs = UserAvailability.objects.filter(user=user).select_related('timeslot')
    for entry in availability_qs:
        day = entry.timeslot.day
        hour = entry.timeslot.start_time.strftime("%H:%M")
        availability[day][hour] = 'O' if entry.is_available else 'X'

    if request.method == 'POST' and 'availability_form' in request.POST:
        availability_data = request.POST.getlist('availability')
        for item in availability_data:
            day, hour, state = item.split(',')
            timeslot = Timeslot.objects.get(day=day, start_time=hour + ":00")
            availability = UserAvailability.objects.get(user=user, timeslot=timeslot)
            availability.is_available = (state == "O")
            availability.save()
        messages.success(request, "Availability updated successfully.")
        return redirect('view_user_profile')

    # Handle competency form if the user is a demonstrator
    if is_demonstrator:
        demonstrator = Demonstrator.objects.get(user=user)
        competencies = Competency.objects.filter(demonstrator=demonstrator)
        competency_form = ProfileCompetencyForm()

        if request.method == 'POST' and 'competency_form' in request.POST:
            competency_form = ProfileCompetencyForm(request.POST)
            if competency_form.is_valid():
                Competency.objects.filter(demonstrator=demonstrator).delete()
                skills = competency_form.cleaned_data['skills']
                for skill in skills:
                    Competency.objects.create(demonstrator=demonstrator, skill=skill)
                messages.success(request, "Competencies updated successfully.")
                return redirect('view_user_profile')

    context = {
        'user_form': user_form,
        'availability': availability,
        'days': days,
        'hours': hours,
        'competencies': competencies,
        'competency_form': competency_form,
        'is_demonstrator': is_demonstrator,
    }
    return render(request, 'profile.html', context)

@login_required
def view_timetable(request):
    """Render the user's timetable, showing all sessions they are involved in as a lecturer or demonstrator.

    :param request: The current HTTP request object.
    :type request: HttpRequest
    :return: A response rendering the timetable page.
    :rtype: HttpResponse
    """
    user = request.user
    days = [(0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"), (4, "Friday")]
    hours = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]

    # Fetch all sessions for which the user is a lecturer or demonstrator
    lecturer_sessions = SessionSchedule.objects.filter(class_session__class_code__lecturer__user=user)
    demonstrator_sessions = SessionSchedule.objects.filter(class_session__allocation__demonstrator__user=user)

    # Dictionary to store the timetable data
    timetable_data = {day[0]: {hour: '' for hour in hours} for day in days}
    conflicts = []

    # Add lecturer sessions to timetable data
    for schedule in lecturer_sessions:
        day = schedule.timeslot.day
        start_time = schedule.timeslot.start_time.strftime("%H:%M")
        cell_content = f"Lecturer\n{schedule.class_session.get_class_code()}\n{schedule.class_session.session_type}"
        if timetable_data[day][start_time]:
            timetable_data[day][start_time] = "Scheduling Conflict. Contact admin"
            conflicts.append((day, start_time))
        else:
            timetable_data[day][start_time] = cell_content

    # Add demonstrator sessions to timetable data
    for schedule in demonstrator_sessions:
        day = schedule.timeslot.day
        start_time = schedule.timeslot.start_time.strftime("%H:%M")
        cell_content = f"Demonstrator\n{schedule.class_session.get_class_code()}\n{schedule.class_session.session_type}"
        if timetable_data[day][start_time]:
            timetable_data[day][start_time] = "Scheduling Conflict. Contact admin"
            conflicts.append((day, start_time))
        else:
            timetable_data[day][start_time] = cell_content

    context = {
        'days': days,
        'hours': hours,
        'timetable_data': timetable_data,
        'conflicts': conflicts,
    }
    return render(request, 'my_timetable.html', context)

@login_required
def edit_competencies(request):
    """Allow demonstrators to edit their competencies by selecting skills from a list.

    :param request: The current HTTP request object.
    :type request: HttpRequest
    :return: A response rendering the edit competencies page with a form.
    :rtype: HttpResponse
    """
    user = request.user
    demonstrator = Demonstrator.objects.get(user=user)

    if request.method == 'POST':
        form = ProfileCompetencyForm(request.POST)
        if form.is_valid():
            # Clear existing competencies
            Competency.objects.filter(demonstrator=demonstrator).delete()
            # Add new competencies
            skills = form.cleaned_data['skills']
            for skill in skills:
                Competency.objects.create(demonstrator=demonstrator, skill=skill)
            return redirect('view_user_profile')  # Redirect to the profile page

    else:
        form = ProfileCompetencyForm(initial={'skills': Competency.objects.filter(demonstrator=demonstrator).values_list('skill', flat=True)})

    return render(request, 'edit_competencies.html', {'form': form})

@login_required
def options(request):
    """Render the options page where users can configure their settings.

    :param request: The current HTTP request object.
    :type request: HttpRequest
    :return: A response rendering the options page.
    :rtype: HttpResponse
    """
    return render(request, 'options.html')

@login_required
def notifications(request):
    """Render the notifications page where users can view their notifications.

    :param request: The current HTTP request object.
    :type request: HttpRequest
    :return: A response rendering the notifications page.
    :rtype: HttpResponse
    """
    return render(request, 'notifications.html')

@login_required
def class_list(request):
    """Display a list of classes (modules) for the logged-in lecturer.

    :param request: The current HTTP request object.
    :type request: HttpRequest
    :return: A response rendering the class list page.
    :rtype: HttpResponse
    """
    user = request.user
    if not user.is_lecturer:
        return redirect('dashboard')
    
    modules = Module.objects.filter(lecturer__user=user)
    context = {
        "modules": modules
    }
    return render(request, 'class_list.html', context)

@login_required
def my_allocations(request):
    """Display a list of session allocations for the logged-in demonstrator.

    :param request: The current HTTP request object.
    :type request: HttpRequest
    :return: A response rendering the allocations page.
    :rtype: HttpResponse
    """
    # Get the current user
    user = request.user
    
    # Ensure the user is a demonstrator
    if not user.is_demonstrator:
        return redirect('dashboard')
    
    # Fetch all allocations for the current demonstrator
    allocations = Allocation.objects.filter(demonstrator__user=user).select_related('class_session__class_code')

    # Prepare the data for the table
    allocation_data = []
    for allocation in allocations:
        session = allocation.class_session
        required_skills = ", ".join([str(skill.skill) for skill in session.requirementskill_set.all()])
        
        allocation_data.append({
            "class_code": session.class_code.class_code,
            "session_type": session.session_type,
            "required_skills": required_skills,
            "details_url": reverse_lazy('module_detail', args=[session.class_code.class_code])
        })

    context = {
        "allocation_data": allocation_data
    }
    return render(request, 'my_allocations.html', context)

@login_required
def module_detail(request, class_code):
    """Display details of a specific module, including its sessions and timetable.

    :param request: The current HTTP request object.
    :type request: HttpRequest
    :param class_code: The class code of the module to be viewed.
    :type class_code: str
    :return: A response rendering the module detail page.
    :rtype: HttpResponse
    """
    module = get_object_or_404(Module, class_code=class_code)
    sessions = ModuleSession.objects.filter(class_code=module)
    timetable = SessionSchedule.objects.filter(class_session__class_code=module)
    
    days = [(0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"), (4, "Friday")]
    hours = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
    
    session_data = []
    for session in sessions:
        session_info = {
            "id": session.id,
            "type": session.session_type,
            "hours": session.get_timeslots().count(),
            "required_demonstrators": session.required_demonstrator,
            "required_skill": ', '.join([str(skill.skill) for skill in session.requirementskill_set.all()])
        }
        session_data.append(session_info)
    
    timetable_data = {day[0]: {hour: '' for hour in hours} for day in days}
    
    for schedule in timetable:
        day = schedule.timeslot.day
        start_time = schedule.timeslot.start_time.strftime("%H:%M")
        session_type = schedule.class_session.session_type
        timetable_data[day][start_time] = session_type
    
    context = {
        "module": module,
        "sessions": session_data,
        "days": days,
        "hours": hours,
        "timetable_data": timetable_data,
    }
    return render(request, 'class_details.html', context)

@login_required
def edit_session(request, session_id):
    """Allow lecturers to edit the details of a specific session, including the number of required demonstrators and relevant skills.

    :param request: The current HTTP request object.
    :type request: HttpRequest
    :param session_id: The ID of the session to be edited.
    :type session_id: int
    :return: A response rendering the edit session page or redirecting to the module detail page on success.
    :rtype: HttpResponse
    """
    session = get_object_or_404(ModuleSession, id=session_id)
    
    if request.method == 'POST':
        form = SessionUpdateForm(request.POST)
        if form.is_valid():
            session.required_demonstrator = form.cleaned_data['required_demonstrators']
            session.save()
            
            new_skill_name = request.POST.get('name')  # 'name' corresponds to the new skill field in your form
            if new_skill_name:
                new_skill, created = Skill.objects.get_or_create(name=new_skill_name)
                session.requirementskill_set.create(skill=new_skill)
            
            session.requirementskill_set.all().delete()
            skills = form.cleaned_data['skills']
            for skill in skills:
                session.requirementskill_set.create(skill=skill)
            
            return redirect('module_detail', class_code=session.class_code.class_code)
    else:
        form = SessionUpdateForm(initial={
            'session_id': session.id,
            'required_demonstrators': session.required_demonstrator,
            'skills': session.requirementskill_set.values_list('skill', flat=True),
        })
    
    context = {
        'session': session,
        'form': form,
    }
    return render(request, 'edit_session.html', context)

@login_required
def create_skill(request):
    """Allow users to create a new skill if it doesn't already exist in the system.

    :param request: The current HTTP request object.
    :type request: HttpRequest
    :return: A redirect response to the referring page or module detail page.
    :rtype: HttpResponseRedirect
    """
    if request.method == 'POST':
        form = SkillCreationForm(request.POST)
        if form.is_valid():
            skill_name = form.cleaned_data['name']
            if not Skill.objects.filter(name=skill_name).exists():
                Skill.objects.create(name=skill_name)
            # Redirect back to the referring page or another default page
            return redirect(request.META.get('HTTP_REFERER', 'module_detail'))
    # If not a POST request, or if form is invalid, just redirect back
    return redirect(request.META.get('HTTP_REFERER', 'module_detail'))