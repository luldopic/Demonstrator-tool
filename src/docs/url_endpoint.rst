===============
URL Endpoints
===============

This document describes the URL endpoints available in the project. Each endpoint corresponds to a specific view and functionality within the system.

.. contents::
   :local:
   :depth: 2

Endpoints Overview
==================

.. _login:

Login
-----
**URL:** ``/login/``

**View:** `UserLoginView` (class-based)

**Description:**  
This endpoint handles user login, displaying the login form and processing authentication.

**Methods:**  
- GET: Display the login form.
- POST: Process login credentials.

.. _logout:

Logout
------
**URL:** ``/logout/``

**View:** `LogoutView` (class-based)

**Description:**  
Logs the user out and redirects them to the login page.

**Methods:**  
- GET: Log the user out and redirect to the login page.

.. _register:

Register
--------
**URL:** ``/register/``

**View:** `user_registration`

**Description:**  
Handles user registration by processing the registration form and creating a new user account.

**Methods:**  
- GET: Display the registration form.
- POST: Process the registration form and create a new user account.

.. _home:

Home
----
**URL:** ``/``

**View:** `home`

**Description:**  
Redirects authenticated users to the dashboard, or renders the login page for unauthenticated users.

**Methods:**  
- GET: Redirect to dashboard or render login page.

.. _dashboard:

Dashboard
---------
**URL:** ``/dashboard/``

**View:** `dashboard`

**Description:**  
Displays the user's dashboard, showing links to relevant sections based on their role (Lecturer or Demonstrator).

**Methods:**  
- GET: Render the dashboard page.

.. _profile:

Profile
-------
**URL:** ``/profile/``

**View:** `view_user_profile`

**Description:**  
Allows users to view and edit their profile, including personal details, availability, and competencies.

**Methods:**  
- GET: Display the profile page with forms for editing user details, availability, and competencies.
- POST: Process updates to user details, availability, and competencies.

.. _timetable:

Timetable
---------
**URL:** ``/timetable/``

**View:** `view_timetable`

**Description:**  
Renders the user's timetable, showing all sessions they are involved in as a lecturer or demonstrator.

**Methods:**  
- GET: Display the timetable page.

.. _options:

Options
-------
**URL:** ``/options/``

**View:** `options`

**Description:**  
Renders the options page where users can configure their settings.

**Methods:**  
- GET: Display the options page.

.. _notifications:

Notifications
-------------
**URL:** ``/notifications/``

**View:** `notifications`

**Description:**  
Renders the notifications page where users can view their notifications.

**Methods:**  
- GET: Display the notifications page.

.. _class_list:

Class List
----------
**URL:** ``/my_classes``

**View:** `class_list`

**Description:**  
Displays a list of classes (modules) for the logged-in lecturer.

**Methods:**  
- GET: Display the list of classes (modules).

.. _my_allocations:

My Allocations
--------------
**URL:** ``/my_allocations``

**View:** `my_allocations`

**Description:**  
Displays a list of session allocations for the logged-in demonstrator.

**Methods:**  
- GET: Display the list of session allocations.

.. _module_detail:

Module Detail
-------------
**URL:** ``/class/<str:class_code>/``

**View:** `module_detail`

**Description:**  
Displays details of a specific module, including its sessions and timetable.

**Methods:**  
- GET: Display the module details page.

.. _edit_session:

Edit Session
------------
**URL:** ``/session/edit/<int:session_id>/``

**View:** `edit_session`

**Description:**  
Allows lecturers to edit the details of a specific session, including the number of required demonstrators and relevant skills.

**Methods:**  
- GET: Display the edit session form.
- POST: Process updates to the session details.

.. _create_skill:

Create Skill
------------
**URL:** ``/create_skill/``

**View:** `create_skill`

**Description:**  
Allows users to create a new skill if it doesn't already exist in the system.

**Methods:**  
- POST: Create a new skill and redirect to the referring page.

.. _edit_competencies:

Edit Competencies
-----------------
**URL:** ``/edit_competencies/``

**View:** `edit_competencies`

**Description:**  
Allows demonstrators to edit their competencies by selecting skills from a list.

**Methods:**  
- GET: Display the edit competencies form.
- POST: Process updates to the demonstrator's competencies.
