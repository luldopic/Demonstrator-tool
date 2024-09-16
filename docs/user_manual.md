  User Manual — Demonstrator Timetabling Tool 0.1 documentation       

[Demonstrator Timetabling Tool](index.html)

  

Contents:

*   [Environment Setup](installation.html)
*   [How to Populate Database with Test Data](usage.html)
*   [URL Endpoints](url_endpoint.html)
*   [User Manual](#)
    *   [Introduction](#introduction)
    *   [Launching the service](#launching-the-service)
    *   [Admin functionality](#admin-functionality)
        *   [User Management](#user-management)
            *   [Admin user creation](#admin-user-creation)
            *   [Normal user creation](#normal-user-creation)
            *   [Editing user information](#editing-user-information)
            *   [Deleting user](#deleting-user)
        *   [Class Management](#class-management)
            *   [Differences between modules and module sessions](#differences-between-modules-and-module-sessions)
            *   [Creating modules](#creating-modules)
            *   [Editing module session skill requirements](#editing-module-session-skill-requirements)
            *   [Creating skills](#creating-skills)
        *   [Allocation Management](#allocation-management)
            *   [Constraint Tiers](#constraint-tiers)
            *   [Ensuring correct allocation slot number](#ensuring-correct-allocation-slot-number)
            *   [Manually allocating demonstrators](#manually-allocating-demonstrators)
            *   [Algorithmically batch allocating demonstrators](#algorithmically-batch-allocating-demonstrators)
            *   [Resetting allocations](#resetting-allocations)
    *   [Regular user functionality](#regular-user-functionality)
        *   [User registration](#user-registration)
        *   [User Login](#user-login)
        *   [User Logout](#user-logout)
        *   [Explaining the dashboard](#explaining-the-dashboard)
            *   [All users](#all-users)
            *   [Lecturers](#lecturers)
            *   [Demonstrators](#demonstrators)
        *   [Managing your profile](#managing-your-profile)
            *   [Updating your availability](#updating-your-availability)
            *   [Updating your demonstrator competencies](#updating-your-demonstrator-competencies)
        *   [Viewing your timetable](#viewing-your-timetable)
        *   [Lecturer functionality](#lecturer-functionality)
            *   [Viewing your classes](#viewing-your-classes)
            *   [Editing class requirements](#editing-class-requirements)
        *   [Demonstrator functionality](#demonstrator-functionality)
            *   [Viewing your allocations](#viewing-your-allocations)
*   [Known Issues](known_issues.html)
*   [API References](modules.html)

[Demonstrator Timetabling Tool](index.html)

*   [](index.html)
*   User Manual
*   [View page source](_sources/user_manual.rst.txt)

* * *

User Manual[](#user-manual "Link to this heading")
===================================================

Welcome to the Demonstrator Timetabling Tool User Manual. This guide is designed to assist administrators, lecturers, and demonstrators in using the site effectively.

*   [Introduction](#introduction)
    
*   [Launching the service](#launching-the-service)
    
*   [Admin functionality](#admin-functionality)
    
    *   [User Management](#user-management)
        
        *   [Admin user creation](#admin-user-creation)
            
        *   [Normal user creation](#normal-user-creation)
            
        *   [Editing user information](#editing-user-information)
            
        *   [Deleting user](#deleting-user)
            
    *   [Class Management](#class-management)
        
        *   [Differences between modules and module sessions](#differences-between-modules-and-module-sessions)
            
        *   [Creating modules](#creating-modules)
            
        *   [Editing module session skill requirements](#editing-module-session-skill-requirements)
            
        *   [Creating skills](#creating-skills)
            
    *   [Allocation Management](#allocation-management)
        
        *   [Constraint Tiers](#constraint-tiers)
            
        *   [Ensuring correct allocation slot number](#ensuring-correct-allocation-slot-number)
            
        *   [Manually allocating demonstrators](#manually-allocating-demonstrators)
            
        *   [Algorithmically batch allocating demonstrators](#algorithmically-batch-allocating-demonstrators)
            
        *   [Resetting allocations](#resetting-allocations)
            
*   [Regular user functionality](#regular-user-functionality)
    
    *   [User registration](#user-registration)
        
    *   [User Login](#user-login)
        
    *   [User Logout](#user-logout)
        
    *   [Explaining the dashboard](#explaining-the-dashboard)
        
        *   [All users](#all-users)
            
        *   [Lecturers](#lecturers)
            
        *   [Demonstrators](#demonstrators)
            
    *   [Managing your profile](#managing-your-profile)
        
        *   [Updating your availability](#updating-your-availability)
            
        *   [Updating your demonstrator competencies](#updating-your-demonstrator-competencies)
            
    *   [Viewing your timetable](#viewing-your-timetable)
        
    *   [Lecturer functionality](#lecturer-functionality)
        
        *   [Viewing your classes](#viewing-your-classes)
            
        *   [Editing class requirements](#editing-class-requirements)
            
    *   [Demonstrator functionality](#demonstrator-functionality)
        
        *   [Viewing your allocations](#viewing-your-allocations)
            

[Introduction](#id4)[](#introduction "Link to this heading")
-------------------------------------------------------------

The Demonstrator Timetabling Tool is designed to streamline the scheduling and management of timetables for educational institutions. This guide covers the essential operations for all users of the system.

[Launching the service](#id5)[](#launching-the-service "Link to this heading")
-------------------------------------------------------------------------------

1.  **Open your terminal or command prompt**.
    
    Navigate to the root directory of your Django project. This is the directory that contains the manage.py file.
    
2.  **Apply migrations**
    
    > This can be done by running the following command:
    > 
    > python manage.py migrate
    
3.  **Run the server**
    
    > This can be done by run the following command:
    > 
    > python manage.py runserver
    

[Admin functionality](#id6)[](#admin-functionality "Link to this heading")
---------------------------------------------------------------------------

The following functionality refers to functionality found at `http://127.0.0.1:8000/admin` on the development server.

### [User Management](#id7)[](#user-management "Link to this heading")

#### [Admin user creation](#id8)[](#admin-user-creation "Link to this heading")

##### **Method 1: Using the command line interface**[](#method-1-using-the-command-line-interface "Link to this heading")

**Prerequisites**

Before you can create an admin user, ensure that you have:

*   The Django project set up and running.
    
*   Applied all necessary migrations to your database.
    

Note

You can apply migrations by running the following command:

python manage.py migrate

**Instructions**

1.  **Open your terminal or command prompt**.
    
    Navigate to the root directory of your Django project. This is the directory that contains the manage.py file.
    
2.  **Run the \`createsuperuser\` command**.
    
    In your terminal, type the following command and press Enter:
    
    python manage.py createsuperuser
    
3.  **Enter the required information**.
    
    You will be prompted to enter the following details:
    
    *   **Username**: Choose a username for the admin account.
        
    *   **Email address**: Provide an email address for the admin user.
        
    *   **Password**: Enter a password for the admin account. You will be asked to confirm it by typing it again.
        
    
    Note
    
    The password must meet Django's password validation criteria. If it does not, you will be prompted to enter a valid password.
    
4.  **Complete the process**.
    
    After you have entered the required information, the admin user will be created. You should see a confirmation message indicating that the user has been successfully created.
    
5.  **Access the Django Admin interface**.
    
    You can now log in to the Django Admin interface using the newly created admin account. To do this:
    
    *   Start the Django development server if it's not already running:
        
        python manage.py runserver
        
    *   Open your web browser and go to `http://127.0.0.1:8000/admin/`.
        
    *   Log in with the username and password you created.
        

Note

Users created using this methods are not assigned any additional roles nor have a default blank user availability tinetable generated

#### [Normal user creation](#id9)[](#normal-user-creation "Link to this heading")

1.  **Accees the Django Admin interface**
    
    > *   Open your web browser and navigate to `http://127.0.0.1:8000/admin/`
    >     
    > *   Log in with a valid admin username and password
    >     
    
2.  **Navigate to the User admin panel**
    
    > *   This can be found in the Users link in the User Management section
    >     
    > *   This can also be access through `http://127.0.0.1:8000/admin/users/user/`
    >     
    
3.  **Create a new user**
    
    > *   The button for this functionality can be found on the top right of the page.
    >     
    
4.  **Enter the required and desired information**
    
    > **Required information**
    > 
    > *   **Username**
    >     
    > *   **Password**
    >     
    > *   **First Name**
    >     
    > *   **Last Name**
    >     
    > *   **Email**
    >     
    > 
    > Username and email have to be unique.
    > 
    > **Optional selection**
    > 
    > *   You may select the staff status alongside the superuser status to create a new admin user.
    >     
    > *   You may select the lecturer and demonstrators role to add those roles to the user.
    >     
    > 
    > Note
    > 
    > Lecturers created with this method will not have a department assigned to them.
    > 
    > Note
    > 
    > Records of the user will be added on the Lecturer and Demonstrator admin page.
    
5.  **Complete the form**
    
    > Once you are satisfied with the form, click one of the save options at the bottom (depending on your needs) to complete process
    

#### [Editing user information](#id10)[](#editing-user-information "Link to this heading")

##### Editing User Information (Name, Email, Password)[](#editing-user-information-name-email-password "Link to this heading")

To edit user information such as name, email, or password, follow these steps:

1.  **Log in to the Admin Interface**:
    
    *   Open your web browser and navigate to the Django Admin interface at `http://127.0.0.1:8000/admin/`.
        
    *   Log in using your admin credentials.
        
2.  **Navigate to Users**:
    
    *   In the admin panel, click on the **Users** section to view the list of registered users.
        
3.  **Select the User to Edit**:
    
    *   Click on the username of the user whose information you want to edit.
        
4.  **Edit User Details**:
    
    *   Update the user's **name**, **email address**, or **password** in the respective fields.
        
5.  **Save Changes**:
    
    *   Once you've made the necessary changes, click the **Save** button at the bottom of the page to apply the updates.
        

##### Creating User Availability slots[](#creating-user-availability-slots "Link to this heading")

In order for the user to have a timetable for which to assign them allocations and schedule to be reflected on the user site, their user availability should be generated. Normally, it should be generated on user creation but in case it doesn't, here's how to create a user availability timetable.

1.  **Navigate to the User section**
    
2.  **Select the user(s)**
    
3.  **Create the user availability**
    
    > *   With the user selected, select the **Create/Update User Availability** in the action dropdown and press go.
    >     
    

##### Changing Lecturer Department[](#changing-lecturer-department "Link to this heading")

To change the department of a lecturer, follow these steps:

1.  **Access the Lecturer's Profile**: - Navigate to the **Lecturers** section in the admin panel.
    
2.  **Edit the Lecturer's Department**: - Select the lecturer whose department you want to change. - In the lecturer's profile, locate the **Department** field. - Write the name of lecturer's department
    
3.  **Save the Changes**: - After updating the department, click **Save** to confirm the changes.
    

##### Changing User Roles[](#changing-user-roles "Link to this heading")

To change the roles assigned to a user:

1.  **Open the User's Profile**: - Go to the **Users** section in the admin interface. - Click on the username of the user whose role you wish to change.
    
2.  **Edit User Roles**: - Scroll down to the **Roles** section within the user's profile. - Add or remove roles as needed by checking or unchecking the appropriate boxes.
    
3.  **Save the Role Changes**: - Click the **Save** button to apply the new roles to the user.
    

Warning

This is desired functionality. However, errors in code do not properly propagate the removal of roles.

##### Removing Roles by Deleting Records (Workaround)[](#removing-roles-by-deleting-records-workaround "Link to this heading")

In some cases, you may need to remove a user's role as a Lecturer or Demonstrator by deleting their records from the respective sections. This method effectively removes the user’s association with those roles.

###### Deleting a Lecturer Record[](#deleting-a-lecturer-record "Link to this heading")

To remove a user from the Lecturer role:

1.  **Navigate to the Lecturers Section**:
    
    *   In the admin panel, click on the **Lecturers** section to view all lecturer records.
        
2.  **Select the Lecturer to Delete**:
    
    *   Locate the lecturer(s) you wish to remove and click on the checkbox next their name
        
3.  **Delete the Lecturer Record**:
    
    *   With the lecturer(s) selected, select the **Delete the selected lecturer** option and press go.
        
    *   Confirm your choice
        
    
    Note
    
    Deleting the lecturer record will not be reflected in the User section. You will have to manually deselect that option for the record to be consistent.
    

###### Deleting a Demonstrator Record[](#deleting-a-demonstrator-record "Link to this heading")

To remove a user from the Demonstrator role:

1.  **Navigate to the Demonstrators Section**:
    
    *   In the admin panel, click on the **Demonstrators** section to view all Demonstrator records.
        
2.  **Select the Demonstrator to Delete**:
    
    *   Locate the demonstrator(s) you wish to remove and click on the checkbox next their name
        
3.  **Delete the Demonstrator Record**:
    
    *   With the demonstrator(s) selected, select the **Delete the selected Demonstrator** option and press go.
        
    *   Confirm your choice
        
    
    Note
    
    Deleting the demonstrator record will not be reflected in the User section. You will have to manually deselect that option for the record to be consistent.
    

#### [Deleting user](#id11)[](#deleting-user "Link to this heading")

To remove a user from the Demonstrator role:

1.  **Navigate to the Users Section**:
    
    *   In the admin panel, click on the **Users** section to view all User records.
        
2.  **Select the User(s) to Delete**:
    
    *   Locate the user(s) you wish to remove and click on the checkbox next their name
        
3.  **Delete the User Record**:
    
    *   With the user(s) selected, select the **Delete the selected User** option and press go.
        
    *   Confirm your choice
        

### [Class Management](#id12)[](#class-management "Link to this heading")

#### [Differences between modules and module sessions](#id13)[](#differences-between-modules-and-module-sessions "Link to this heading")

In the context of this system, module and module sessions refer to different responsibility within the application. A **module** represents an academic subject that is taught over the course of a semester. A **module session** represents a group of classes within the module with the same requirements in terms of number of demonstrators and their needed skills. For example, a lab requiring 2 demonstrator with a beginner level in Python.

#### [Creating modules](#id14)[](#creating-modules "Link to this heading")

1.  **Navigate to the Modules Section**
    
    > *   After logging in, locate the **Modules** section in the Django admin panel.
    >     
    > *   Click on **Modules** to view the list of existing modules.
    >     
    
2.  **Create a New Module**
    
    > *   **Click the "Add Module" button** (usually located at the top right of the Modules page) to create a new module.
    >     
    > *   Fill in the following details for the new module:
    >     
    >     > *   **Class Code**: Enter a unique identifier for the module. This is typically a short code, such as "CS101".
    >     >     
    >     > *   **Name**: Enter the full name of the module, such as "Introduction to Computer Science".
    >     >     
    >     > *   **Lecturer**: Select the lecturer responsible for the module from the dropdown list. If no lecturer is assigned yet, you can leave this field blank.
    >     >     
    >     > *   **Semester**: Select the semester during which the module will be taught from the dropdown list.
    >     >     
    >     
    
    Note
    
    Ensure that the **Class Code** is unique across all modules. The system will not allow duplicate class codes.
    
3.  **Save the Module**
    
    > *   Once all the required fields are filled in, **click the "Save" button** at the bottom of the form to create the module.
    >     
    > *   If the save is successful, you will be redirected to the list of modules, where the new module should now appear.
    >     
    
4.  **Assign Module Sessions (Optional)**
    
    > *   After creating the module, you may want to add specific sessions (e.g., lectures, tutorials, labs) associated with the module.
    >     
    > *   Navigate to the **Module Sessions** section in the admin panel and create sessions linked to your newly created module.
    >     
    >     > *   **Session Type**: Choose the type of session, such as Lecture, Tutorial, or Lab.
    >     >     
    >     > *   **Required Demonstrators**: Specify the number of demonstrators required for the session, if applicable.
    >     >     
    >     > *   **Test Session**: Indicate whether this session is a test session.
    >     >     
    >     
    > *   **Save the session** to link it to the module.
    >     
    
5.  **Create a Schedule for the Module Session (Optional)**
    
    > *   Find the object number of your module session (found at the top of the module session's detail page)
    >     
    > *   Navigate to the **Session Schedule** section of the admin panel and create a session schedule linked to your newly created module session at the timeslot you require.
    >     
    > *   **Save** to save the record in the database
    >     
    > *   Repeat as needed to fill the schedule as needed
    >     
    > 
    > Note
    > 
    > There cannot be duplicated scheduled slots within a module session. If you have two sessions happening concurrently with the similar requirement, a new module session must be created
    > 
    > Note
    > 
    > This is a temporary solution. A proper method of creating a schedule will be created in the future.
    

#### [Editing module session skill requirements](#id15)[](#editing-module-session-skill-requirements "Link to this heading")

This section is to change the skill required by a demonstrator for a module session.

1.  **Navigate to the Requirement skill Section**:
    
    > *   After logging in, locate the **Requirement Skill** section in the Django admin panel.
    >     
    > *   Click on **Requirement Skill** to view the list of existing requirement skill.
    >     
    
2.  **Create a New Requirement Skill**:
    
    > *   Using the object number of your module session, create a requirement skill choosing the skill (include skill level) required by the demonstrator(s).
    >     
    > *   If the new skill, you are looking is not present, see the instructions to creating a skill below.
    >     
    
3.  [\*\*](#id2)Save your changes
    

Note

Requirements skills are not reset upon creation of a new requirement. If requirements change, locate the requirements tied to the module session previous and delete by selecting it and delete using action **Delete selected requirement skills** at the top of the table

#### [Creating skills](#id16)[](#creating-skills "Link to this heading")

1.  **Navigate to Skills Section**
    
    > This is seperate from the Requirement Skill section
    
2.  **Create the skill**
    
    > *   Click the button on the top right of the page.
    >     
    > *   Write of the skill you wish to add.
    >     
    > *   Save
    >     
    

Note

When creating a skill, three versions of the skill is created with one for each of the skill levels (Beginner, Intermediate, Expert)

### [Allocation Management](#id17)[](#allocation-management "Link to this heading")

#### [Constraint Tiers](#id18)[](#constraint-tiers "Link to this heading")

The allocation system uses a system of constraint tiers to improve allocations.

##### Hard Constraints[](#hard-constraints "Link to this heading")

Hard constraints are the most stringent rules that must be strictly followed during the allocation process. If any hard constraint is violated, the allocation is considered invalid.

*   **No Double Booking**: Ensures that a demonstrator is not scheduled for more than one session at the same time.
    
*   **Availability**: Verifies that the demonstrator is available during the timeslot of the session.
    
*   **Unapproved Allocations**: Ensures that the allocation has not been previously approved and locked.
    

These constraints are non-negotiable and are enforced first during the allocation process to eliminate any demonstrators who cannot meet these basic requirements.

##### Primary Soft Constraints[](#primary-soft-constraints "Link to this heading")

Primary soft constraints are less rigid than hard constraints but are still considered highly important. They aim to ensure a minimum acceptable standard for the allocation. If these constraints are not met, the allocation is not ideal but may still be considered depending on the availability of alternatives.

*   **Minimum Demonstrator Count**: Ensures that a session has at least half of the required number of demonstrators.
    
*   **Beginner Skill Level**: Verifies that the demonstrators have at least a basic (beginner) level of the skills required for the session.
    

##### Secondary Soft Constraints[](#secondary-soft-constraints "Link to this heading")

Secondary soft constraints are the next level of flexibility, focusing on optimizing the allocation once the primary constraints have been satisfied. These constraints aim for a better fit but are not critical to the success of the session.

*   **Exact Demonstrator Count**: Ensures that the session has the exact number of demonstrators required.
    
*   **Required Skill Level or Higher**: Ensures that the demonstrators meet or exceed the required skill level for the session.
    

#### [Ensuring correct allocation slot number](#id19)[](#ensuring-correct-allocation-slot-number "Link to this heading")

While the system should ensure that correct number of allocation slots are created when change the number of demonstrators is changed in the module session page, here are the steps to ensure this is correct.

1.  **Navigate to the Module Session admin section**
    
2.  **Select the module session for which you wish to ensure**
    
    > You may ensure for all module sessions by checking the select all box at the top of the table.
    
3.  **Ensure the allocation slots**
    
    > *   Within the actions selection at the top, select the **Ensure Correct Allocation** options and press go
    >     
    

Note

In the case, where there are most allocation slots than required, the last one will be removed.

#### [Manually allocating demonstrators](#id20)[](#manually-allocating-demonstrators "Link to this heading")

1.  **Navigate to the Allocation Section admin section**
    
2.  **Select the allocation slot you wish change**
    

Note

A search functionality is currently missing and will be implemented in the future.

3.  **Select the demonstrator you wish to assign**
    

Warning

They are correctly not checks ensuring that a demonstrator assign manually will meet the requirements needs in terms of availability and skill.

4.  **Check approved if satisfied and save**
    

Note

Selecting the approved check prevents the demonstrator from being changed if it is batch selected for automatic allocation.

#### [Algorithmically batch allocating demonstrators](#id21)[](#algorithmically-batch-allocating-demonstrators "Link to this heading")

1.  **Select the allocation(s) for which you wish to assign a demonstrator.**
    
2.  **Allocate the demonstrator automatically**
    
    > *   Within the actions dropdown at top, select the **Automatically assign demonstrators** option and press go
    >     
    

Note

Depending on the number of demonstrators within the system and the number of allocations you have selected to be allocate, this may take a while. Please do not close the page as the process in ongoing.

3.  **Try again with a smaller number of slots (Optional)**
    
    > *   If the process fails with all the selected allocations, the system wasn't able to find a fitting match for all allocations slots.
    >     
    

Note

If the process fails with only one allocation slot selected, there are no fitting demonstrators in the database meeting the minimum hard requirements

Note

There are currently no indications of the progress of the allocation process expect a small buffer in the tab icon. Furthermore, there are no indications of failures. This will be fixed in a future version.

#### [Resetting allocations](#id22)[](#resetting-allocations "Link to this heading")

1.  **Select the allocation(s) for which you wish to remove the demonstrator**
    
2.  **Reset the allocation**
    
    > *   Within the action dropdown at the top, select the **Unallocate demonstrators** option and press go
    >     
    

[Regular user functionality](#id23)[](#regular-user-functionality "Link to this heading")
------------------------------------------------------------------------------------------

The following functionality refers to functionality found at `http://127.0.0.1:8000/` on the development server.

### [User registration](#id24)[](#user-registration "Link to this heading")

1.  **Navigate to the registration page**
    
    > *   This can be done going to the login page (url: `/login`) and pressing register or by going to the url: `/register`
    >     
    
2.  **Fill in the form**
    
3.  **Press register**
    
    > *   If you are successful, you will be redirected to your dashboard
    >     
    

Note

There are currently no messages when there is an issue with the form (i.e. invalid password, email or username are already existing)

Warning

There is a major issue in the user creation and authentication process wherein the user will be created in the database despite successfully reaching the dashboard. This means none of the changes they make in their profile are saved and the user is unable to log back in once they log out. Furthermore, users created using the **createsuperuser** are inconsistently able to login using this form. A workaround is to log in using the admin site and then navigate to `/dashboard`

### [User Login](#id25)[](#user-login "Link to this heading")

1.  **Navigate to the login page**
    
    > *   You should be directed to the login page if you access the user site if you are logged in.
    >     
    > *   You may access the site directly on `/login`
    >     
    
2.  **Enter your credentials**
    

Warning

There is currently an issue where users not created using the **createsuperuser** method described in the admin section are unable to login.

### [User Logout](#id26)[](#user-logout "Link to this heading")

1.  **Click the log out button at the top right of the page**
    

Note

There is currently no confirmation dialog. Be careful when navigating near that button.

### [Explaining the dashboard](#id27)[](#explaining-the-dashboard "Link to this heading")

Depending on your role(s), you will be presented with options on your dashboard.

#### [All users](#id28)[](#all-users "Link to this heading")

All users will have access to their profile (found on **My Profile** on the menu bar) and their timetable **My Timetable**.

#### [Lecturers](#id29)[](#lecturers "Link to this heading")

Lecturers will have access to the list of classes for which they are responsible on **My Classes**

#### [Demonstrators](#id30)[](#demonstrators "Link to this heading")

Demonstrators will have access to the list of module sessions for which they have been allocated on **My Allocations**

### [Managing your profile](#id31)[](#managing-your-profile "Link to this heading")

Your profile is seperated into 3 different forms

1\. User information form which include name and email address. .. note:: There is an issue where changes to your name and email address are not saved.

2\. Availability form which presents as a timetable with green boxes for available and red for not available. .. note:: If the boxes present as white, the system hasn't correctly created a blank timetable for you. Create your availability using the method described in the admin section.

3\. Competencies which presents as list of skills you are competent in. .. note:: This is only viewable by demonstrators.

Warning

These are three seperate forms and pressing save in one of the section will not save changes in the other sections.

#### [Updating your availability](#id32)[](#updating-your-availability "Link to this heading")

1.  **Arrange your availability as desired**
    
    > You can toggle your availability from available to not available and vice versa but clicking on the cell. May require double clicking.
    
2.  **Save**
    
    > Your changes are only saved if you press the save availability button.
    

Note

The system does not verify whether a change from not available to available is valid. You may still be assigned as a lecturer or demonstrator during that timeslot.

#### [Updating your demonstrator competencies](#id33)[](#updating-your-demonstrator-competencies "Link to this heading")

1.  **Click on the Edit Competencies button**
    
    > This will show a list of all skills registered in the database.
    
2.  **Select all skills you are competent at**
    
    > Select the skill at the highest level of competency you are at. You may select lower levels but this is unnecessary.
    

Note

You must selected all skills including the skills which have been previously saved. Failure to do so will remove these skills from your competency list.

3.  **Save**
    
    > Your changes are only saved if you press the save competencies button.
    

### [Viewing your timetable](#id34)[](#viewing-your-timetable "Link to this heading")

Your timetable with be displayed from **My Timetable** on the dashboard or on `/timetable`. This will show all classes you are responsible for as a lecturer and demonstrator. If there are any scheduling conflict, the timeslot will display as red with the message "Scheduling conflict. Contact admin". Your availability will not be reflected here.

### [Lecturer functionality](#id35)[](#lecturer-functionality "Link to this heading")

#### [Viewing your classes](#id36)[](#viewing-your-classes "Link to this heading")

Your modules will be displayed as a list from **My Classes** on the dashboard or on `/my_classes` You may click on **See class details** to view more infomation on that module.

Note

There is an issue where the session type is not properly displayed on the class detail page. It will be display if you click the edit button.

Note

It is currently not possible for the lecturer to alter the schedule of the module.

#### [Editing class requirements](#id37)[](#editing-class-requirements "Link to this heading")

1.  **Navigate to the module you wish to alter**
    
2.  **Navigate to the edit page by clicking on the button corresponding to the module session for which you wish change requirements**
    
3.  **Select the number of demonstrators you require**
    

4\. **Select the skills you wish your demonstrators to have from the list** .. note:: This page is currently missing a search functionality.

5.  **Add a new skill (Optional)**
    
    > *   If the skill you require is not present, click the add skill button, fill the form with the name of the skill you require and press save.
    >     
    > *   The new skill will now be found on the list. You must select it to add it to your requirements.
    >     
    
6.  **Save your changes**
    
    *   You will now be redirected to the module page.
        
    

### [Demonstrator functionality](#id38)[](#demonstrator-functionality "Link to this heading")

#### [Viewing your allocations](#id39)[](#viewing-your-allocations "Link to this heading")

Your allocations will be displayed on **My Allocations** from the dashboard or by navigating to `/my_allocations` This will display all module sessions for which you have been assigned along with the skills required by that session.

Further details can be found by clicking the details button.


* * *

© Copyright 2024, Ludovic Picard.

