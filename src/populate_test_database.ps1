./reset_database.ps1
py manage.py makemigrations
py manage.py migrate

# Creating new admin
$env:DJANGO_SUPERUSER_USERNAME = "admin"
$env:DJANGO_SUPERUSER_EMAIL = "admin@example.com"
$env:DJANGO_SUPERUSER_PASSWORD = "qwert"

py manage.py createsuperuser --noinput

# Populate database
py manage.py populate_default_timeslots
py manage.py populate_test_skills test_data/skills.csv
py manage.py populate_modules test_data/CIS_modules.csv
py manage.py populate_sessions --test
py manage.py generate_test_users --total 50
py manage.py generate_test_users --demonstrator 200
py manage.py generate_test_users_availability
py manage.py populate_competencies --test
py manage.py create_test_timetables --all
