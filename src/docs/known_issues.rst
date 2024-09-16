.. _known-issues:

===============
Known Issues
===============

as of version v 0.1.0

Authorisation and Authentication
----------------------------------

- Registration page does not display error messages when there is an issues with the form submitted
- Logging in with users not created using the `createsuperuser` method is currently bugged. Users are unable to login if they are regularly created
- Users using the `createsuperuser` method are inconsistently able to login into the user site.
    - Logging in through the admin site then navigate to /dashboard seems to be a workaround
- User who successfully register on the user site are redirected to their dashboard but their records are not consistently reflected on the database. It may not reflected on the database for a while or never reflect at all. They also don't have a user availability and any changes to their profiles are not saved.

Admin panel inlines
--------------------

- The module session inline in the admin site fails to properly recognise skills when adding or changing requirements
    - Change the requirement in the requirement skills admin section
- The module and module session inlines in the admin site is missing a way of viewing the schedule tied to them
    - Navigate to the session schedule page and filter the class by class code in the search bar

- The demonstrator inlines in the admin site failsto properly recognise skills when adding or changing competencies
    - Change the competencies in the competency admin section

- The user inlines in the admin site is missing a way of viewing the user availability tied to the user
    - Navigate to the user availability page and filter the user by name

Permissions
-----------

- The button to view the classes details from the allocation page on the user site redirects to the same page as the lecturer page thus allowing a demonstrator to change the details despite not having the permissions to\\

Class Management
------------------

- Currently, it is difficult to create a schedule for a module. The current method of creating a schedule requires the admin to find the corresponding module sessions object number and one by one, create a session schedule for that module session.
- There is an issue where the session type not properly displayed on the class detail list on the user site.

Allocation Management
----------------------

- Batch allocation of demonstrator takes a while and leaving the pages while the process is ongoing sometimes prevents allocation. Multithreading is required in the future to allow for better concurrency.
- There is no indication of the progress of the allocation process. 
- There is no indication of the allocation system failing to allocate.
- The allocation page is missing a search bar to filter by class code. To circumvent, go to the Module session admin page, select the module session you wish to view the allocations for and select `View Allocations of Selected Session` in the action dropdown.

Accessibility
--------------
- There are no confirmation dialog for any of the functionality in the user site (including logging out)
- There are no accessibility options in either site and the options button in the user site is no functional.
- The notification system is non-functional
- There are missing messages in the case of errors in forms (i.e login or registration)
- Skills can't be filtered or searched in the user site when changing competencies or requirement skills 

User Management
---------------------
- If a user changes their availability from not available to available using either the admin site or the user site, the system doesn't check whether that change is valid (e.g. user is still a demonstrator in that timeslot)
- User availability is not fetching in the profile if the user is not a demonstrator (in the demonstrator model not just checked in the user details) despite useravailability not being tied to being a demonstrator model. As a workaround, assign the user as a demonstrator and set all availability as not available in order for them to not be selected as a demonstrator.
