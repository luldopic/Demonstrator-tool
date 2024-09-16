rm db.sqlite3
Get-ChildItem -Recurse -Filter *.py -Include migrations | Where-Object { $_.Name -ne '__init__.py' } | Remove-Item                                                  
Get-ChildItem -Recurse -Filter *.pyc -Include migrations | Remove-Item
py manage.py makemigrations
py manage.py migrate
py manage.py populate_default_timeslots                                                                                          