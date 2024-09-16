from django.urls import path
from django.contrib.auth.views import LogoutView
from users.views import user_views

urlpatterns = [
    path('login/', user_views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', user_views.user_registration, name='register'),
    path('', user_views.home, name='home'),
    path('dashboard/', user_views.dashboard, name='dashboard'),
    path('profile/', user_views.view_user_profile, name='view_user_profile'),
    path('timetable/', user_views.view_timetable, name='view_timetable'),
    path('options/', user_views.options, name='options'),
    path('notifications/', user_views.notifications, name='notifications'),
    path('my_classes', user_views.class_list, name = 'class_list'),
    path('my_allocations', user_views.my_allocations, name='my_allocations'),
    path('class/<str:class_code>/', user_views.module_detail, name='module_detail'),
    path('session/edit/<int:session_id>/', user_views.edit_session, name='edit_session'),
    path('create_skill/', user_views.create_skill, name='create_skill'),
    path('edit_competencies/', user_views.edit_competencies, name='edit_competencies')
]