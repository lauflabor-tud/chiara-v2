from fabric.api import lcd, local
from chiara.settings.common import SITE_ROOT

def refresh():
    """
    Refreshs the apache server with updated data of the project.
    """
    with lcd(SITE_ROOT):
        local('python manage.py syncdb')
        local('python manage.py collectstatic')
        local('sudo service apache2 restart')