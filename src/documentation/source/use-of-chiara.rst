How to use Chiara
=================

.. sidebar:: Questions?
    :subtitle: Please contact us at:
    
    mmaus@sport.tu-darmstadt.de
    dominik.reis@stud.tu-darmstadt.de

.. contents::


Mount your webfolder to your local disk
---------------------------------------
The following steps will show you how to connect your local disk with your webfolder. You have to choose the manual depending on your operating system.

Linux
'''''
**Mount**

1. Install the package *davfs*. If you use a distribution based on *Debian* you can install it as follows::

    sudo apt-get install davfs2

#. Create an empty directory in which the data will be mapped. For the example */home/user/mnt* you have to type::

    mkdir /home/user/mnt

#. Mount your webfolder into this directory. You can do this with the following command.::

    sudo mount -t davfs -o uid=1000 http://130.83.212.83/chiara-webdav/ /home/user/mnt

#. Enter your chiara name and password.

#. Now you can find the content of your webfolder in */home/user/mnt*.

**Unmount**

    If you want to unmount */home/user/mnt* for example you have to type::
    
        sudo umount /home/user/mnt

Mac Os X
''''''''
**Mount**

1. Open **Finder**, click **Go** and then click **Connect to Server...**.
#. Insert *http://130.83.212.83/chiara-webdav/* in the **Server Address** box.
#. If you want to add this server address to **Favorite Servers**, click the **+** button.
#. Click **Connect**.
#. Enter your chiara name and password and click **Connect**. 
#. Open **Finder**.
#. You can launch your webfolder by clicking it under **SHARED** in the sidebar.

**Unmount**

1. Open **Finder**.
#. Find your webfolder under **SHARED** in the sidebar and click the eject symbol next to its name.

Windows
'''''''
**Mount**

1. Click the **Start** button and then right-click **Computer**.
#. Click **Map network drive**...
#. In the **Drive** list, choose a drive letter.
#. Type *\\\\130.83.212.83\\chiara-webdav\\* in the **Folder** box.
#. To connect every time you log on to your computer, select the **Reconnect at logon** check box.
#. Click **Finish**.
#. When the *Windows Security* window has been opened, enter your chiara name and password and click **OK**. 
#. Open Computer by clicking the **Start** button, and the clicking **Computer**.
#. You can launch your webfolder by open the drive letter you have chosen above.

**Unmount**

1. Open Computer by clicking the **Start** button, and the clicking **Computer**.
#. Right-click on your webfolder.
#. Click **Disconnect**.


Workflow
--------

Put data into the repository
''''''''''''''''''''''''''''
The following steps will show you how to put data into the repository to share these with your partners.

1. Copy the new directory to your webfolder.
#. Be sure that the new dirctory contains a `description.txt`_ file placed under *<collection>/_chiara/description.txt*.
#. Launch Chiara website.
#. Choose the tab `my shared folder`_ and add the respective directory to collections.
#. Choose the tab `manage my collections`_ and customize the permissions.


Get data into your webfolder
''''''''''''''''''''''''''''
The following steps will show you how to get shared data of your partners into your webfolder.

1. Launch Chiara website.
#. Choose the tab `retrieve new collections`_ and search new collections by dint of some tags.
#. After you have found the respective collection, you can choose a location of the collection in your web folder by entering a favored path. 
#. Choose **subscripe & download** in the drop down menu and click **OK**.
#. Take a look into your webfolder.


Connect to ownCloud
'''''''''''''''''''
The following steps will show you how to connect Chiara with ownCloud. This is a big advantage because huge files can be added to and downloaded from the repository easily.

1. Launch Chiara website.
#. Choose the tab `my shared folder`_ and add an ownCloud directory by clicking the button in the upper right area.
#. Now there is a new directory called *ownCloud* in your webfolder.
#. Choose the option **mount owncloud** and click **OK**.
#. Enter your ownCloud name and password.
#. Your root directory of ownCloud is mounted in the ownCloud directory of Chiara.

| Now it is possible to add files from this directory to the repository (explained in `Put data into the repository`_). 
| It is also possible to download files from the repository into this directory (explained in `Get data into your webfolder`_). In this case, you have to enter *ownCloud* as favored path.


Interface description
---------------------
The Chiara web page comes with five tabs. In the following you can find the description of each one.

News
''''
This tab shows all the news like new users, new groups, new collections, updated collections, etc. But you can only see news of collections of which you've got reading access at least.


My shared folder
''''''''''''''''
This tab shows the content of your mounted webfolder. You can walk throug it and apply different options to the directories in it.

**add to collections** 
    Adds the respective directory to the repository to share it with your partners. You have subsribed this collection automatically. For permission handling see `Manage my collections`_. The directory must contain a `description.txt`_ file.

**unsubscribe**
    Unsubscribes an subsribed directory. But this will not remove the directory from the repository.

**push local revision**
    Pushs the local changes of a subsribed collection to the repository with a new revision number. You have to comment your actual changes.

    *Note:* You need writing permissions for this option.

**update to revision**
    Updates a subscribed collection in your webfolder in the chosen revision. 

    *Note:* Your local changes will be overwritten.
    
**remove from webfolder**
   Remove the respective directory in the webfolder. You have to unsubsribe the collection before you can do this.

It is also possible to integrate your ownCloud directory in the webfolder. First you have to create an ownCloud dirctory with button in the upper right area. After this you have different options for the created directory.

**mount owncloud**
   Mount your ownCloud root directory by entering your ownCloud name and password.
   
**unmount owncloud**
   Unmount your ownCloud directory.

**remove from webfolder**
   Remove the ownCloud directory in the webfolder. You have to unmount the ownCloud directory before you can do this.

You have the same options as above inside the ownCloud directory. So you can add any directories from the ownCloud directory to the repository.


Retrieve new collections
''''''''''''''''''''''''
For finding collection, you can search in the repository by some tags like *title*, *author*, *topic*, *keywords*, etc. If you choose more than one tag, these will be combined conjunctive.
The tags are defined in the `description.txt`_. If you do not insert anything, all permitted collections will be found.

After you have found the respective collection, you can subscribe and download it into any favored path in your webfolder. Therefore it is possible to download a collection into your ownCloud directory.

*Note:* You can only find collections for which you have reading permissions at least.


Manage my collections
'''''''''''''''''''''
This tab shows all added or subscribed collections. You can apply different options to the collections.

**download**
    Downloads the respective collection in the newest revision into your webfolder.

**permissions**
    You can give users and groups read/write access to the respective collection.
 
    +---------------------------+-----------+-----------+----------------+
    |                           | no access | read only | read and write |
    +===========================+===========+===========+================+
    | **update to revision**    |    no     |    yes    |       yes      |
    +---------------------------+-----------+-----------+----------------+
    | **push local revision**   |    no     |    no     |       yes      |
    +---------------------------+-----------+-----------+----------------+
    | **find in search**        |    no     |    yes    |       yes      |
    +---------------------------+-----------+-----------+----------------+
    | **download option**       |    no     |    yes    |       yes      |
    +---------------------------+-----------+-----------+----------------+
    | **permissions option**    |    no     |    no     |       yes      |
    +---------------------------+-----------+-----------+----------------+
    
    You can also give public users read access to the respective collection.

**unsubscribe**
    Unsubscribes the subscribed collection. But this will not remove the collection from the repository.


My account
''''''''''
You can logout or choose preferences (like changing password, etc.) under the drop down menu of the **My account** tab.


Additional Information
----------------------

description.txt
'''''''''''''''
Each collection must contain a *description.txt*  before you can add it to the repository. The file has to be placed under *<collection>/_chiara/description.txt*.
It contains the information of the respective directory. You can define an abstract, some details and search tags. This also helps to retrieve the directory easier.

It can be structured as follows::

   ### Abstract ###
   This collection is a short example to show how a collection can be look. 
   
   
   ### Details ###
   The directory structure is as follows:
   
   img/
       Contains all example pictures. Please insert only images in PNG.
   
   docs/
       Contains all example documents.
   
   
   ### Tags ###
   topic:         Documentation
   project:       Chiara
   authors:       Dominik Reis
   creation_date: 08.2014           # Format: dd.mm.yyyy / mm.yyyy / yyyy
   keywords:      doc, workflow

Download an example: :download:`description.txt <resources/description.txt>`

