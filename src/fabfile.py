from fabric.api import lcd, local
import os, shutil
from chiara.settings.common import SITE_ROOT

# Print variables
RESET_MYSQL = """
===========
Reset MySQL
===========
You have to do the first steps manually:
    - Logon MySQL:        mysql -u root -p
    - Delete database:    DROP DATABASE <db_name>;
    - Create database:    CREATE DATABASE <db_name>;
    - Give permissions:   grant all on <db_name>.* to <user>@<host> identified by <password>;
"""
RESET_SOUTH = """
===============================================
Reset South migration files and sync with MySQL
===============================================
"""
CREATE_SUPERUSER = """
=================
Create superuser
=================
"""


main_apps = ['authentication', 'collection',]


def refresh():
    """
    Refreshs the apache server with updated data of the project.
    """
    with lcd(SITE_ROOT):
        local('python manage.py syncdb')
        local('python manage.py collectstatic')
        local('sudo service apache2 restart')
        
        
def reset_db():
    """
    Reset the database
    """
    
    # Reset in MySQL
    print RESET_MYSQL
    user_input = ""
    while(user_input!='yes'):
        user_input = raw_input('Are you finished? Type yes: ')
    
    # Reset in Django
    with lcd(SITE_ROOT):
        print RESET_SOUTH
        for app in main_apps:
            if(os.path.exists(os.path.join(SITE_ROOT, app, 'migrations'))):
                shutil.rmtree(os.path.join(SITE_ROOT, app, 'migrations'))
            local('python manage.py schemamigration ' + app + ' --initial')  
        local('python manage.py syncdb')  
        for app in main_apps:
            local('python manage.py migrate ' + app)
        print CREATE_SUPERUSER
        local('python manage.py createsuperuser')
        