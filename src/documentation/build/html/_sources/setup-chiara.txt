Setting up Chiara
=================

.. sidebar:: Questions?
    :subtitle: Please contact us at:

    mmaus@sport.tu-darmstadt.de
    dominik.reis@stud.tu-darmstadt.de

.. contents::


Compatibility
-------------
*Chiara* is only compatible with *Linux*. So you have to set up a Linux server.

Setup per remote access
-----------------------
The following steps will show you what you need to do to configure Chiara on a server from somewhere else.

Linux/Mac Os X
''''''''''''''
1. Open *Terminal* and access to the server with *SSH* by typing::

    ssh <user>@<server-address>

#. Answer at the security warning with **yes**.
#. Insert your password.
#. Now you are logged on to the server.

     
Windows
'''''''
1. Dowload *PuTTY* at http://www.putty.org/.
#. Run *putty.exe*.
#. Fill-out the fields **Host name (or IP address)** and **Port**.
#. Choose at connection type **SSH**.
#. *Optional:* If you want to save this configuration, you have to insert in the **Saved Sessions** field an arbitrary name and click **Save**.
#. Click **Open**.
#. When the *PuTTY Security Alert* Window opens, click **Yes**.
#. Enter your username and password.
#. Now you are logged on to the server.


Install & configure Apache
--------------------------
The following description is for distributions based on *Debian*. You have to execute all commands with **sudo**. 

1. Install *Apache*. ::
   
    apt-get install apache2
 
#. Install *wsgi* package for connecting *Apache* with *Django*. ::

    apt-get install libapache2-mod-wsgi
   
#. Enable necessary modules. ::
    
    a2enmod wsgi dav dav_fs auth_digest
    
.. _chiara.conf:

4. Navigate to */etc/apache2/sites-available* and create a chiara configuration file like this: :download:`chiara.conf <resources/chiara.conf>`

#. Link this file to *sites-enabled* and use *a2ensite <sitename>* to enable the website. ::
    
    ln -s /etc/apache2/sites-available/chiara /etc/apache2/sites-enabled/chiara
    
    a2ensite chiara
    
.. _000-default.conf:
 
6. Modify your default configuration */etc/apache2/sites-available/000-default.conf* by adding the following to it: :download:`000-default.conf <resources/000-default.conf>`

#. Create a Chiara directory in Apache's home. ::

    mkdir /var/www/chiara

#. Link Chiara webdav to Apache. *<path-to-chiara>* means the path where Chiara is located (e.g. */qnap/chiara*). ::

    ln -s <path-to-chiara>/src/webdav /var/www/chiara/webdav

#. Add user and group *chiara* and set permissions. ::
    
    addgroup chiara
    
    adduser chiara --ingroup chiara

    usermod -aG chiara chiara
    
    usermod -aG chiara www-data

    chown -cR www-data:chiara <path-to-chiara>

    find <path-to-chiara> -exec chmod 775 {} +

#. `Install & configure Chiara`_.

#. Restart apache::

    service apache2 restart

#. Open your browser and insert your server adress configured in `chiara.conf`_ to check if it works (e.g. *http://130.83.212.83/chiara*). 


Install & configure Chiara
--------------------------

Install requirements
''''''''''''''''''''
You need pip for installing the requirements of Chiara. If you do not have it, you can install it with::

    sudo apt-get install python-pip
    
Navigate to *<path-to-chiara>/requirements/pip* and execute::

    sudo pip install -r common.txt


Configure Chiara
''''''''''''''''
1. Next you have to configure Chiara. The configuration file is located at *<path-to-chiara>/src/chiara/settings/local.py*. Adapt this file to your personal interest. The important setting parameters are:

   **SERVER_ADDRESS**
      The URL of the server (e.g. '130.83.212.83').
   
   **DATABASES**
      The database configuration. If you want to use SQLite, set::
   
       DATABASES = {
           'default': {
               'ENGINE': 'django.db.backends.sqlite3',
               'NAME': os.path.join(PROJECT_DIR, 'db.sqlite3'),
               'USER': '',
               'PASSWORD': '',
               'HOST': '',             # Empty for localhost.
               'PORT': '',             # Empty string for default.
           }
       }
   
      If you want to use an other database, look at https://docs.djangoproject.com/en/1.6/ref/databases/.
   
   **STATIC_ROOT**
      The location, where the static files (like CSS, JavaScript, Images) are located. This depends on your configuration in `chiara.conf`_. (e.g. */var/www/chiara/static/*)
       
   **STATIC_URL**
      The URL for static files. (e.g. */chiara/static/*)

.. _CODE_ADMIN:

   **CODE_ADMIN** 
      The Chiara user name of the code admin.
   

2. Navigate to *<path-to-chiara>/src/*.

#. You have to execute the following command for creating the database. After you were asked to create a new superuser, answer with *yes* and follow the instructions. It is important to enter the same user name which is configured as `CODE_ADMIN`_:: 
    
    sudo ./manage.py syncdb --all

#. Move the static files of Chiara into the apache directory with::

    sudo ./manage.py collectstatic
    

Integrate ownCloud
''''''''''''''''''
For integrating ownCloud to Chiara, you have to append the file */etc/fstab* with::

   <path-of-ownCloud-webdav> <path-to-chiara>/src/webdav/<chiara-username>/ownCloud davfs user,noauto,rw 0 0

| But you have to replace *<path-of-ownCloud-webdav>*, *<path-to-chiara>* and *<chiara-username>*. 
| *<path-of-ownCloud-webdav>* is http://localhost/owncloud/remote.php/webdav for example.


Administration
''''''''''''''
1. For managing users, groups, collections, etc. you have to log in Chiara. 
#. Click the **Administration** tab in the footbar.
#. All data of the database can be managed in the displayed administration interface. 

*Note:* If you want to add a new user, you have to add the ownCloud path for the new user additionally. See `Integrate ownCloud`_.


Overview: Implementation of Chiara
----------------------------------
Chiara is implemented in the web application framework *Django*. The documentation is written in *reStructuredText*.

Django
''''''
There are three django applications of the *Django* project:

**authentication**
    This app manages all users and groups with their permissions to the collection. It is also responsible for authentication on the chiara webpage.
    
**collection**
    This app contains the structure and logic of collections and their directories, files, tags, etc.

**log**
    This app contains all news (like adding or updating a collection).

reStructeredText
''''''''''''''''
The chiara html documentation is located in *<path-to-chiara>/doc* and is linked to *<path-to-chiara>/web/doc*. It will be built with *reStructeredText* and compiled with *Sphinx*. If you want to install Sphinx, you can do this as follows::

    sudo apt-get install sphinx-common sphinxbase-utils sphinx-doc sphinxsearch

The *index.rst* is the main file and combine all documentation parts like *use-of-chiara.rst*, *setup-chiara.rst*, etc. 


