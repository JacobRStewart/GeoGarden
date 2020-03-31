Installation:

Make sure you have the latest version of python3 installed, and run pip to install required packages:
pip install required packages [see requirements.txt]

Set your FLASK_APP variable to the app before running:

In Unix Bash (Linux, Mac, etc.):
$ export FLASK_APP=geogarden.py

In Windows CMD:
> set FLASK_APP=geogarden.py

In Windows PowerShell:
> $env:FLASK_APP = "geogarden.py"


Then, initialize the database and run the application:

flask initdb
flask run