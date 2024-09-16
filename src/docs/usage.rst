How to Populate Database with Test Data
=======================================

Overview
--------

This documentation provides detailed instructions and descriptions for the various scripts used to populate the test database with essential data required for development and testing purposes.

.. contents::
   :local:
   :depth: 2

To facilitate testing, a script is provided that populates the database with test data. This is particularly useful for running tests on a consistent dataset or simulating real-world scenarios.

**Script**: `populate_test_database.ps1`

Description
~~~~~~~~~~~~~~~~~

The `populate_test_database.ps1` script inserts a predefined set of test data into the database. This data is useful for testing various functionalities of the application without having to manually insert data each time.

Usage
~~~~~~~~~~~

1. Ensure that the virtual environment is activated and the database is correctly set up.
2. Execute the script from the PowerShell command line:

.. code-block:: shell

   ./populate_test_database.ps1

What the Script Does
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Connects to the database specified in your environment settings.
- Inserts a set of test data, including sample users, products, transactions, or other relevant entities.
- Can be run multiple times to reset the test data to its original state.

Additional Notes
~~~~~~~~~~~~~~~~~~~~~~

- This script is intended for development and testing purposes only. Do not use it in a production environment.
- If modifications to the test data set are needed, update the script accordingly to reflect the new data requirements.


Documentation Structure
------------------------

- Each script is documented with its purpose, usage, and a description of its functionality.
- The scripts can be run individually to populate different parts of the test database.

.. note::
   Ensure that the required CSV files are formatted correctly and located in the appropriate directories before running the scripts.


Scripts Overview
----------------

This section provides an overview of each script used to populate the test database.

generate_test_users.py
----------------------

**Purpose**: Generates random users for testing purposes.

**Usage**:

.. code-block:: shell

   python manage.py generate_test_users --total <number_of_users>

To generate test demonstrators:

.. code-block:: shell

   python manage.py generate_test_users --demonstrator <number_of_demonstrators>

**Description**:
- This script uses the `Faker` library to generate realistic fake user data.
- Users can specify the number of test users or demonstrators to create.
- The generated users have unique usernames and emails, and can be flagged as demonstrators or lecturers.


generate_test_users_availability.py
-----------------------------------

**Purpose**: Generates availability records for users marked as fake for all available time slots.

**Usage**:

.. code-block:: shell

   python manage.py generate_test_users_availability

**Description**:
- This script creates `UserAvailability` records for each fake user across all available time slots.
- It ensures that no duplicate availability records are created.
- The script provides feedback on the number of users for whom availability was created.


add_new_skill.py
----------------

**Purpose**: Adds a new skill to the `Skill` database.

**Usage**:

.. code-block:: shell

   python manage.py add_new_skill <skill_name>

**Description**:
- This script accepts the name of a skill as an argument and creates a new skill entry in the database.
- If the skill is successfully created, a confirmation message is displayed.


populate_test_skills.py
-----------------------

**Purpose**: Populates the database with a list of skills from a CSV file.

**Usage**:

.. code-block:: shell

   python manage.py populate_test_skills <csv_file>

**Description**:
- This script reads skill data from a specified CSV file and creates new skill records in the database.
- It provides feedback on the success or failure of the operation.


populate_modules.py
-------------------

**Purpose**: Populates the database with a list of modules from a CSV file.

**Usage**:

.. code-block:: shell

   python manage.py populate_modules <csv_file>

**Description**:
- This script reads module data from a CSV file and either creates new module records or updates existing ones in the database.
- The script can handle semester information and associate modules with the correct semester.


populate_sessions.py
--------------------

**Purpose**: Populates the database with a list of module sessions from a CSV file or generates random module sessions for testing purposes.

**Usage**:

To populate from a CSV file:

.. code-block:: shell

   python manage.py populate_sessions <csv_file>

To randomly generate sessions:

.. code-block:: shell

   python manage.py populate_sessions --test

**Description**:
- The script can either populate sessions from a CSV file or randomly generate them for testing.
- It handles session types like lectures, tutorials, and labs, and ensures no scheduling conflicts.


populate_competencies.py
------------------------

**Purpose**: Populates the database with a list of competencies from a CSV file or randomly generates competencies for test demonstrators.

**Usage**:

To populate from a CSV file:

.. code-block:: shell

   python manage.py populate_competencies <csv_file>

To randomly generate competencies:

.. code-block:: shell

   python manage.py populate_competencies --test

**Description**:
- The script can either populate competencies from a CSV file or generate them randomly for test demonstrators.
- It uses a biased random distribution to assign skill levels and removes duplicate skills.


create_test_timetables.py
-------------------------

**Purpose**: Generates random timetables for testing purposes.

**Usage**:

To generate a timetable for a specific module:

.. code-block:: shell

   python manage.py create_test_timetables --class-code <class_code>

To generate timetables for all modules:

.. code-block:: shell

   python manage.py create_test_timetables --all

**Description**:
- This script creates realistic timetables based on constraints such as session types and maximum teaching hours.
- It ensures that the generated timetables do not exceed specified constraints and do not contain scheduling conflicts.


Documentation Structure
------------------------

- Each script is documented with its purpose, usage, and a description of its functionality.
- The scripts can be run individually to populate different parts of the test database.

.. note::
   Ensure that the required CSV files are formatted correctly and located in the appropriate directories before running the scripts.

