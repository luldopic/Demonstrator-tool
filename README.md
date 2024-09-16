# Demonstrator Timetabling Tool

Welcome to the **Demonstrator Timetabling Tool** repository! This project is designed to streamline the allocation and management of demonstrators for academic institutions, ensuring optimal timetabling and scheduling.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [Acknowledgements](#acknowledgements)

## Features

- **Automated allocation**: Automatically assigns demonstrators based on availability, skillset, and constraints.
- **Manual adjustments**: Manually adjust assignments and override automated decisions.
- **Constraint-based scheduling**: Supports hard and soft constraints to improve scheduling accuracy.
- **Multi-role management**: Handle multiple roles such as lecturers, demonstrators, and administrators.
- **Real-time updates**: Reflects changes in schedules and allocations instantly.
- **Comprehensive dashboard**: A user-friendly dashboard for demonstrators and lecturers to view their allocations.

## Installation

Follow these steps to set up the project in your local development environment.

### Prerequisites

Ensure the following are installed on your system:
- **Python 3.x**
- **PowerShell** (for Windows setup)
- **PostgreSQL** (for database management)

### Steps to Set Up the Environment

1. **Clone the repository**:
    ```bash
    git clone https://github.com/username/Demonstrator-tool.git
    cd Demonstrator-tool
    ```
2. **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```
3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4. **Set up the database**:
    ```bash
    python manage.py migrate
    ```
5. **Run the development server**:
    ```bash
    python manage.py runserver
    ```

For more detailed instructions, refer to the [Installation Guide](docs/installation.md).

## Usage

Once the server is running, the application can be accessed by navigating to `http://127.0.0.1:8000/` in your browser.

### Key Features
- **Admin Interface**: Manage user roles, create and assign classes, and view schedules from `http://127.0.0.1:8000/admin/`.
- **Demonstrator Interface**: Demonstrators can view their allocated classes and update their availability.
- **Lecturer Interface**: Lecturers can manage class requirements and review demonstrator assignments.

For detailed usage information, refer to the [User Manual](docs/user_manual.html).

## Contributing

We welcome contributions to improve the Demonstrator Timetabling Tool! If you wish to contribute:
1. Fork the repository.
2. Create a new feature branch:
    ```bash
    git checkout -b feature-name
    ```
3. Commit your changes and push to your fork.
4. Open a pull request.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

Special thanks to all contributors and testers who helped make this project possible.
