.. _environment-setup:

==================
Environment Setup
==================

This section provides a step-by-step guide for setting up the development environment for this project. The setup process involves resetting or creating a virtual environment, installing required dependencies, initializing the database, and running the development server. Ensure that you have the necessary tools installed on your machine before proceeding.

.. contents::
   :local:
   :depth: 2

.. _prerequisites:

Prerequisites
=============

Before setting up the environment, ensure that the following prerequisites are met:

- **Windows Operating System**: These instructions are tailored for a Windows environment using PowerShell.
- **Python 3.x**: Ensure Python 3.x is installed and accessible via the command line.
- **PowerShell**: The scripts provided are written for PowerShell.

.. _setup-steps:

Steps to Set Up the Environment
===============================

1. **Reset or Create the Virtual Environment**

   To ensure a clean environment, use the provided `reset_venv.ps1` script to reset (or create) and activate the virtual environment.

   .. code-block:: shell

      ./reset_venv.ps1

   **Description**: This script resets the Python virtual environment in the project directory, creating it if it doesn’t exist, and then activates it.

   **Usage**:

   - Open PowerShell.
   - Navigate to the project directory.
   - Execute the script:

   .. code-block:: shell

      ./reset_venv.ps1

   **What the Script Does**:

   - Removes the existing virtual environment directory (if it exists).
   - Creates a new virtual environment in a directory named `venv`.
   - Activates the virtual environment, preparing it for use.

2. **Install Required Dependencies**

   Once the virtual environment is activated, the next step is to install the required Python packages. This is handled by the `reinstall_requirement.ps1` script.

   .. code-block:: shell

      ./reinstall_requirement.ps1

   **Description**: This script installs or reinstalls the Python dependencies listed in the `requirements.txt` file.

   **Usage**:

   - Ensure the virtual environment is activated.
   - Execute the script:

   .. code-block:: shell

      ./reinstall_requirement.ps1

   **What the Script Does**:

   - Checks if the `requirements.txt` file is present in the project directory.
   - Installs the packages listed in the `requirements.txt` file using `pip`.

3. **Reset and Initialize the Database**

   To ensure that the database is correctly set up, the 'reset_database.ps1' script is provided. The `reset_database.ps1` script helps with resetting and initializing the database.

   .. code-block:: shell

      ./reset_database.ps1

   **Description**: This script resets the database to its initial state, which is useful for development and testing.

   **Usage**:

   - Ensure the virtual environment is activated.
   - Execute the script:

   .. code-block:: shell

      ./reset_database.ps1

   **What the Script Does**:

   - Drops the existing database (if applicable) and recreates it.
   - Runs initial migrations or scripts to set up the database schema.
   - Optionally, seeds the database with initial data.

4. **Run the Development Server**

   After setting up the environment and initializing the database, you can start the development server using the `run_server.ps1` script.

   .. code-block:: shell

      ./run_server.ps1

   **Description**: This script starts the development server, allowing you to interact with the application through a web browser.

   **Usage**:

   - Ensure the virtual environment is activated.
   - Execute the script:

   .. code-block:: shell

      ./run_server.ps1

   **What the Script Does**:

   - Starts the Django development server.
   - The site can be accessed at the following URLs:
   
      - **User Site**: `http://127.0.0.1:8000/`
      - **Admin Site**: `http://127.0.0.1:8000/admin`

   After running the script, open a web browser and navigate to the appropriate URL depending on whether you need to access the user-facing site or the admin interface.

.. _list-of-requirements:

List of Requirements
=====================

The following Python packages are required for the project. These packages are listed in the `requirements.txt` file and can be installed using the provided script.

.. code-block:: text

   django==3.2.9
   pytest>=7.0.0
   djangorestframework>=1.0
   markdown>=1.0
   django-filter>=20.0
   django-bootstrap-v5>=1.0
   djangorestframework-simplejwt>=1.0
   whitenoise>=1.0
   faker>=1.0
   numpy>=1.0
   coverage>=1.0
   sphinx>=1.0
   sphinx-rtd-theme>=1.0
   sphinxcontrib-django>=1.0

.. _additional-notes:

Additional Notes
================

- **Virtual Environment**: Always ensure the virtual environment is activated before running any project-related commands to avoid conflicts with system-wide Python packages.
- **Database Reset**: Use the database reset script cautiously, as it will remove all data in the database.
- **Script Execution Policy**: If you encounter an error about the execution policy, you may need to change the policy to allow running scripts:

  .. code-block:: shell

     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

.. _troubleshooting:

Troubleshooting
===============

- **Script Not Running**: If a script fails to run, check that you have permission to execute PowerShell scripts on your machine and that the execution policy is correctly configured.
- **Dependency Issues**: If there are issues with installing dependencies, ensure that the `requirements.txt` file is up to date and correctly formatted.

