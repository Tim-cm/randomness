Campus Ledger - Setup and Testing

REQUIREMENTS
Python 3.x installed on your machine.

1. CREATE PROJECT FOLDER
mkdir simpleProj(Creates the top-level folder)
cd simpleProj(moves into the top-level folder created)
download the whole project folder under code in github as a zip file.
Extract this zipfile in the folder simpleProj created
The simpleProj folder should contain the config folder, mainapp folder and the files : .gitignore, README.md, manage.py and requirements.txt

3. CREATE VIRTUAL ENVIRONMENT
python3 -m venv .venv(on linux and mac)
python -m venv .venv(on windows cmd or powershell)
(Creates an isolated Python environment named .venv, used to keep this project's packages separate from other projects.)

4. ACTIVATE THE VIRTUAL ENVIRONMENT
mac/Linux: source .venv/bin/activate
Windows(PowerShell): .venv\Scripts\Activate.ps1
Windows(cmd): .venv\Scripts\activate.bat
(Must be run in every new terminal session before using pip or python for this project.)

5. UPGRADE PIP
python -m pip install --upgrade pip
(Updates pip to its latest version to avoid installation errors.)

6. INSTALL FROM REQUIREMENTS
pip install -r requirements.txt
(Installs every package listed in requirements.txt at the recorded versions.)

7. APPLY DATABASE MIGRATIONS
python manage.py migrate
(Creates the SQLite database file and all required tables.)

8. CREATE AN ADMIN LOGIN
python manage.py createsuperuser
(Prompts for username, email, and password. Used to log into /admin/.)

9. RUN THE DEVELOPMENT SERVER
python manage.py runserver
(Starts the site at http://127.0.0.1:8000/)

Admin: http://127.0.0.1:8000/admin/
go to /admin/, log in, and add:
- Campuses (your 5 campuses e.g. Main Campus, Chiromo campus, KNH Campus etc)
- Split rules (percentages for each income group TITHE/COMBINED_OFFERING/LCB_OFFERING/LOOSE_OFFERING, subgroups local/overall/ckc)
This data is required before adding income, since income splitting depends on it.

Dashboard: http://127.0.0.1:8000/
Report: http://127.0.0.1:8000/report/
Stop the server with Ctrl+C.

RUNNING TESTS

Run all tests:
python manage.py test
(Runs every automated test in the project and reports pass/fail.)

Run one test class only:
python manage.py test mainapp.tests.ReportTests
(Runs only the tests inside the ReportTests class.)

Run one specific test:
python manage.py test mainapp.tests.ReportTests.test_closing_balance_equals_opening_plus_local_total
(Runs a single named test method.)

PROJECT STRUCTURE
simpleProj/
  .venv/            virtual environment (not committed to git)
  config/           Django project settings, urls, wsgi/asgi
  mainapp/          the app: models, views, forms, reports.py, templates, tests
  manage.py         command-line entry point for all django commands
  requirements.txt  pinned package list
  db.sqlite3        local database file (not committed to git)
