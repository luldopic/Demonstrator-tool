# Demonstrator Timetabling Tool

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [Usage](#usage)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Project Overview

The Demonstrator Timetabling Tool is a web-based application designed to assist educational institutions in managing and optimizing timetables. The tool allows administrators, lecturers, and demonstrators to efficiently schedule, allocate, and manage sessions, ensuring that resources are utilized effectively.

## Features

- **User Management**: Admins can manage user accounts and assign roles.
- **Timetable Management**: Lecturers can create and manage timetables for their sessions.
- **Demonstrator Allocation**: Automatic or manual allocation of demonstrators to sessions based on availability and competencies.
- **Notifications**: Real-time notifications for schedule changes and updates.
- **Feedback System**: Collect feedback from students on sessions to improve future planning.

## Getting Started

### Prerequisites

Before you begin, ensure you have met the following requirements:

- **Operating System**: Windows (PowerShell is required), macOS, or Linux.
- **Python**: Version 3.x installed and accessible via command line.
- **Database**: PostgreSQL or any other compatible SQL database.

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/demonstrator-timetabling-tool.git
   cd demonstrator-timetabling-tool

2. **Set up a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a **.env** file in the root directory and add the necessary environment variables, such as database credentials.

5. **Initialise database**
```bash
python manage.py migrate
```

### Running the Application

1. **Start the development server**
```bash
python manage.py runserver
```

2. **Access the application**
Open a web browser and navigate to http://127.0.0.1:8000/.

