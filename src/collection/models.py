from __future__ import division
from django.db import models, IntegrityError
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist
import os, utils.path, utils.hash, re, sys
import shutil, ConfigParser
from chiara.settings.common import WEBDAV_DIR, COLLECTION_INFO_DIR, COLLECTION_DESCRIPTION_FILE, COLLECTION_TRAITS_FILE, REPOSITORY_DIR, BASH_DIR
from chiara.settings.local import PUBLIC_USER, OWNCLOUD_DIR_NAME
from authentication.models import User, UserPermission, GroupPermission, Subscription
from log.models import News
from utils import enum
import utils.date
from collection import info
from exception.exceptions import *
from progress.models import Progress, ProgressParam, start_progress, update_progress

import logging
logger = logging.getLogger(__name__)



class Collection(models.Model):
    """The Collection model represent a collection of directories
    and files. It contains a root directory with the name, revision
    and further information."""

    identifier = models.IntegerField(verbose_name=u'ID')
    revision = models.IntegerField(verbose_name=u'revision')

    directory = models.OneToOneField('collection.Directory', 
                                     related_name='collection')
    
    abstract = models.TextField(verbose_name=u'abstract', blank=True)
    details = models.TextField(verbose_name=u'details', blank=True)
    comment = models.TextField(verbose_name=u'comment', blank=True)
    
    tags = models.ManyToManyField('collection.Tag', 
                                  verbose_name=u'tags',
                                  related_name='collections',
                                  blank=True)
    
    public_access = models.BooleanField(verbose_name=u'public access',
                                    default=False)
    
    @property        
    def name(self):
        return self.directory.name
    
    @property
    def authors(self):
        return [t.value for t in self.tags.filter(key=enum.Tag.AUTHOR)]

    @property
    def topics(self):
        return [t.value for t in self.tags.filter(key=enum.Tag.TOPIC)]
    
    def get_revision(self, revision):
        """Returns the collection with the given revision. If the revision greater than
        the maximum revision than returns the maximum revision."""
        max_revision = self.get_all_revisions().aggregate(Max('revision'))['revision__max']
        if revision >= max_revision:
            revision = max_revision
        return Collection.objects.get(identifier=self.identifier, revision=revision)
    
    def get_all_revisions(self):
        """Returns a list of collection revisions."""
        return Collection.objects.filter(identifier=self.identifier)
    
    def get_file(self, path):
        """Returns the file of the given relative path."""
        [dirs, f] = os.path.split(path)
        sub_dir = self.get_dir(dirs)
        if(sub_dir):
            f = sub_dir.files.filter(name=f)
            # check if file exists
            if(f):
                return f[0]
        return None
    
    def get_dir(self, path):
        """Returns the directory of the given relative path."""
        split_path = utils.path.no_slash(path).split("/")
        dirs = split_path[1:]
        sub_dir = self.directory
        # walk down to last directory
        for d in dirs:
            sub_dir = sub_dir.sub_directories.filter(name=d)
            # check if directory exists
            if(sub_dir):
                sub_dir = sub_dir[0]
            else:
                return None
        return sub_dir


    @staticmethod
    def get_all_public_collections():
        return [c for c in Collection.objects.all() if c.public_access]
    
    @staticmethod
    def retrieve_collections(user, tags):
        """Search the collections in the repository by filtering with the given tags 
        and permissions of the user."""
        logger.debug("anonym: " + str(user.is_anonymous()))
        # get all public collections in newest revision
        public_collections = [c for c in Collection.get_all_public_collections() if c==c.get_revision(sys.maxint)]
        
        if user.is_anonymous():
            permitted_collections = []
            subscribed_collections = []
        else:
            # get all collections in newest revision which the user is permitted
            permitted_collections = [c for c in user.get_all_permissible_collections() if c==c.get_revision(sys.maxint)]
            # remove all subscribed collections
            subscribed_collections = [c.get_revision(sys.maxint) for c in user.subscriptions.all()]
        collections = list((set(public_collections) | set(permitted_collections)) - \
                           set(subscribed_collections))
        # filter the collections with each of the given tags
        for (key, value) in tags:
            if value.strip()=="":
                continue
            values = value.split(" ")
            if key==enum.Tag.TITLE:
                collections = [c for c in collections 
                               if 0.5 <= (len([v for v in values if re.search(v, c.directory.name, re.IGNORECASE)]) / len(values))]
            elif key==enum.Tag.ABSTRACT:
                collections = [c for c in collections 
                               if 0.5 <= (len([v for v in values if re.search(v, c.abstract, re.IGNORECASE)]) / len(values))]
            elif key==enum.Tag.AUTHOR:
                collections = [c for c in collections for t in c.tags.filter(key=key)
                               if 0.66 <= (len([v for v in values if re.search(v, t.value, re.IGNORECASE)]) / len(values))]
            elif key==enum.Tag.TOPIC:
                collections = [c for c in collections for t in c.tags.filter(key=key)
                               if 0.5 <= (len([v for v in values if re.search(v, t.value, re.IGNORECASE)]) / len(values))]
            elif key==enum.Tag.PROJECT:
                collections = [c for c in collections for t in c.tags.filter(key=key)
                               if 0.5 <= (len([v for v in values if re.search(v, t.value, re.IGNORECASE)]) / len(values))]
            elif key==enum.Tag.CREATION_DATE_MIN:
                collections = [c for c in collections for t in c.tags.filter(key=enum.Tag.CREATION_DATE)
                               if utils.date.get_date(t.value) >= utils.date.get_date(value)]
            elif key==enum.Tag.CREATION_DATE_MAX:
                collections = [c for c in collections for t in c.tags.filter(key=enum.Tag.CREATION_DATE)
                               if utils.date.get_date(t.value) <= utils.date.get_date(value)]
            elif key==enum.Tag.PUBLISHING_DATE_MIN:
                collections = [c for c in collections
                               if c.get_revision(1).directory.date_modified >= utils.date.get_date(value)]
            elif key==enum.Tag.PUBLISHING_DATE_MAX:
                collections = [c for c in collections
                               if c.get_revision(1).directory.date_modified <= utils.date.get_date(value)]
            elif key==enum.Tag.LAST_MODIFICATION_DATE_MIN:
                collections = [c for c in collections
                               if c.get_revision(sys.maxint).directory.date_modified >= utils.date.get_date(value)]
            elif key==enum.Tag.LAST_MODIFICATION_DATE_MAX:
                collections = [c for c in collections
                               if c.get_revision(sys.maxint).directory.date_modified <= utils.date.get_date(value)]
            elif key==enum.Tag.KEYWORD:
                collections = [c for c in collections for t in c.tags.filter(key=key)
                               if 0.5 <= (len([v for v in values if re.search(v, t.value, re.IGNORECASE)]) / len(values))]
        return collections
                
    
    def add_to_collection(self, user, rel_path):
        """Adds the given user directory to collection repository 
        with all subdirectories and files. Also sets the user permission
        and subscription."""
        # read description file
        desc_parser = info.parse_description(user, rel_path)
        
        # Create root directory and save it with all subdirectories and files
        item = os.path.basename(rel_path)
        root_dir = Directory(revision=1,
                             name=item,
                             user_modified=user,
                             size=WebFolder.get_dir_size(user, rel_path))
        root_dir.save()
        info.create_traits(user, rel_path, root_dir.identifier, 1)
        root_dir.size = WebFolder.get_dir_size(user, rel_path)
        root_dir.save_recursive(user, rel_path)
        root_dir.save()
        
        # Set collection attributes
        self.directory = root_dir
        self.revision = 1
        self.save()
        self.abstract = desc_parser.get_abstract()
        self.details = desc_parser.get_details()
        self.comment = "Add the collection to the repository."
        self.save()
        for (key,value) in desc_parser.get_tags():
            try:
                tag = Tag.objects.get(key=key, value=value)
            except ObjectDoesNotExist:
                tag = Tag(key=key, value=value)
                tag.save()
            self.tags.add(tag)
    
        # Set user access
        permission = UserPermission(collection=self,
                                    user=user,
                                    permission=enum.Permission.WRITE)
        permission.save()
        
        # Set user subscription
        subscription = Subscription(collection=self,
                                    user=user)
        subscription.save()
        
        # Update news log
        content =   "A new collection <b>" + self.name + "</b> was added to the repository.\n" + \
                    "<i><b>Abstract:</b>\n" + self.abstract + "</i>"
        news = News(user=User.get_current_user(),
                    content=content,
                    collection=self)
        news.save()

    
    def push_local_revision(self, user, rel_path, prev_col, comment):
        """Push the local revision to the repository."""
        
        prev_max_revision = Collection.objects.filter(identifier=prev_col.identifier).aggregate(Max('revision'))['revision__max']
        
        # collection is at newest revision
        if prev_col.revision == prev_max_revision:
            # read description file
            desc_parser = info.parse_description(user, rel_path)
            
            # Create root directory and update it with the local revision
            item = os.path.basename(rel_path)
            root_dir = Directory(identifier=prev_col.directory.identifier,
                                 revision=prev_col.revision+1,
                                 name=item,
                                 user_modified=user,
                                 size=WebFolder.get_dir_size(user, rel_path))
            root_dir.save()
            info.create_traits(user, rel_path, root_dir.identifier, root_dir.revision)
            root_dir.size = WebFolder.get_dir_size(user, rel_path)
            root_dir.save()
            root_dir.push_recursive(user, rel_path, prev_col.directory)
            
            if root_dir.hash == prev_col.directory.hash:
                root_dir.delete()
                raise NoLocalChangesException()
            else:
                # Set collection attributes
                self.identifier = prev_col.identifier
                self.directory = root_dir
                self.revision = prev_col.revision+1
                self.save()
                self.abstract = desc_parser.get_abstract()
                self.details = desc_parser.get_details()
                self.comment = comment
                self.save()
                for (key,value) in desc_parser.get_tags():
                    try:
                        tag = Tag.objects.get(key=key, value=value)
                    except ObjectDoesNotExist:
                        tag = Tag(key=key, value=value)
                        tag.save()
                    self.tags.add(tag)
            
                # Set user access
                UserPermission.update(self)
                GroupPermission.update(self)
                
                # Set user subscription
                subscription = Subscription(collection=self,
                                            user=user)
                subscription.save()
                
                # Update news log
                content =   "The collection <b>" + self.name + "</b> was updated to revision " + \
                            str(self.revision) + ".\n" + "<i><b>Comment:</b>\n" + self.comment + "</i>"
                news = News(user=User.get_current_user(),
                            content=content,
                            collection=self)
                news.save()
        # collection is not at newest revision
        else:
            raise NotNewestRevisionException()
        
    
    def download(self, user, rel_path, task_id):
        """Download the collection into the given directory of the user's webfolder."""
        # start progress
        data = {ProgressParam.TOTAL : self.directory.size}
        start_progress(task_id, data)
        
        # copy files into the webfolder
        rel_dir_path = os.path.join(rel_path, self.directory.name)
        progress = Progress(task_id, self, rel_dir_path)
        WebFolder.remove_dir_recursive(user, rel_dir_path)
        WebFolder.create_directory(user, rel_dir_path)
        self.directory.download_recursive(user, rel_dir_path, progress)
        # Set user subscription
        subscription = Subscription(collection=self,
                                    user=user)
        subscription.save()

    
    def download_public(self, rel_path, task_id):
        """Download the collection into the given directory of the public folder."""
        # start progress
        data = {ProgressParam.TOTAL : self.directory.size}
        start_progress(task_id, data)
        
        # copy files into the public folder
        rel_dir_path = os.path.join(rel_path, self.directory.name)
        progress = Progress(task_id, self, rel_dir_path)
        PublicFolder.remove_dir_recursive(rel_dir_path)
        PublicFolder.create_directory(rel_dir_path)
        self.directory.download_recursive_public(rel_dir_path, progress)
    

    def unsubscribe(self, user):
        """Unsubscribe the collection of the user."""
        try:
            subscription = Subscription.objects.get(user=user, collection=self)
            subscription.delete()
        except ObjectDoesNotExist:
            pass
        
        
    def subscribe(self, user):
        """Subscribe the collection of the user."""
        subscription = Subscription(collection=self,
                                        user=user)
        subscription.save()


    def update_public_access(self, access):
        """Set public access to all revisions of the collection.
        Parameter access is a boolean value."""
        if(self.public_access!=access):
            self.public_access = access
            self.save()
            for c in self.get_all_revisions():
                c.public_access = access
                c.save()
                
            # Update news log
            if access:
                readable_access="public"
            else:
                readable_access="not public"
            content =   "The permissions of collection <b>" + self.name + "</b> were changed.\n" + \
                        "The collection is " + readable_access + "."
            news = News(user=User.get_current_user(),
                        content=content,
                        collection=self)
            news.save()
            

    def update_user_permission(self, user, permission):
        """Grant the given user the given permission of this collection."""
        if permission:
            if UserPermission.objects.filter(user=user, collection=self):
                p = UserPermission.objects.get(user=user, collection=self)
                p.permission = permission
            else:
                p = UserPermission(user=user, collection=self, permission=permission)
            p.save_all_revisions()
        else:
            p = UserPermission.objects.get(user=user, collection=self)
            p.delete_all_revisions()
            
        # Update news log
        content =   "The user permissions of collection <b>" + self.name + "</b> were changed.\n" + \
                    "The user <b>" + user.user_name + "</b> has " + utils.enum.Permission.get_readable_permission(permission) + " access."
        news = News(user=User.get_current_user(),
                    content=content,
                    collection=self)
        news.save()


    def update_group_permission(self, group, permission):
        """Grant the given group the given permission of this collection."""
        if permission:
            if GroupPermission.objects.filter(group=group, collection=self):
                p = GroupPermission.objects.get(group=group, collection=self)
                p.permission = permission
            else:
                p = GroupPermission(group=group, collection=self, permission=permission)
            p.save_all_revisions()
        else:
            permission = GroupPermission.objects.get(group=group, collection=self)
            permission.delete_all_revisions()

        # Update news log
        content =   "The group permissions of collection <b>" + self.name + "</b> were changed.\n" + \
                    "The group <b>" + group.group_name + "</b> has " + utils.enum.Permission.get_readable_permission(permission) + " access."
        news = News(user=User.get_current_user(),
                    content=content,
                    collection=self)
        news.save()
        

    def save(self, *args, **kwargs):
        """Find id before initial a directory and check required fields."""
        # initial collection
        if not self.id and self.revision==1:
            # raise exception if no directory
            if self.directory_id==None:
                raise IntegrityError("collection_collection.directory may not be NULL")
            # get id for the collection and save it
            self.identifier = self.directory.identifier
            super(Collection, self).save()
        # update directory
        else:
            # raise exception if no directory
            if self.directory_id==None:
                raise IntegrityError("collection_collection.directory may not be NULL") 
            else:
                super(Collection, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return unicode(self.directory)
    
    class Meta:
        unique_together = (("identifier", "revision"),)
        verbose_name = "collection"
        verbose_name_plural = "collections"



class Directory(models.Model):
    """The Directory model represent a directory of a collection.
    The root directory is the primary key of a collection."""

    identifier = models.IntegerField(verbose_name=u'ID')
    revision = models.IntegerField(verbose_name=u'revision')
    name = models.CharField(verbose_name=u'name', max_length=120)
    
    sub_directories = models.ManyToManyField('collection.Directory', 
                                             verbose_name=u'sub directories',
                                             related_name='parent_directories',
                                             blank=True)
    files = models.ManyToManyField('collection.File', 
                                   verbose_name=u'files',
                                   related_name='parent_directories',
                                   blank=True)

    user_modified = models.ForeignKey('authentication.User', 
                                      verbose_name=u'user who modified',
                                      related_name='directory_modified')
    date_modified = models.DateTimeField(verbose_name=u'last modified', auto_now_add=True)
     
    size = models.BigIntegerField(verbose_name=u'size')
 
    hash = models.CharField(verbose_name=u'hash', max_length=64)
 
    def is_root(self):
        """Check if this directory is the root directory."""
        return len(self.parent_directories.all())==0
 
        
    def save_recursive(self, user, rel_path):
        """Save all subdirectories and files of this directory and 
        create connections to this directory."""
        item_hashs = []
        # Save recursive files and directories
        for item in WebFolder.list_dir(user, rel_path):
            rel_item_path = os.path.join(rel_path, item)
            if WebFolder.is_file(user, rel_item_path):                
                f = File(revision=1, 
                         name=item, 
                         user_modified=user, 
                         size=WebFolder.get_file_size(user, rel_item_path),
                         hash=utils.hash.hash_file(WebFolder.get_abs_path(user, rel_item_path))
                         )
                f.save()
                WebFolder.copy_file_to_repository(user, rel_item_path, WebFolder.get_repository_file_name(f.identifier, f.revision))
                self.files.add(f)
                item_hashs.append(f.hash)
            elif WebFolder.is_dir(user, rel_item_path):
                d = Directory(revision=1,
                              name=item,
                              user_modified=user,
                              size=WebFolder.get_dir_size(user, rel_item_path))
                
                d.save()
                d.save_recursive(user, rel_item_path)
                self.sub_directories.add(d)
                item_hashs.append(d.hash)
        # Set directory hash
        self.hash = utils.hash.hash_dir(self.name, item_hashs)
        self.save()
    
    
    def push_recursive(self, user, rel_path, prev_dir):
        """Push the local changes of this directory as a new revision."""
        
        item_hashs = []
        
        for item in WebFolder.list_dir(user, rel_path):
            rel_item_path = os.path.join(rel_path, item)
            # item is a file
            if WebFolder.is_file(user, rel_item_path):
                prev_f = prev_dir.files.filter(name=item)
                # file is new
                if not prev_f:
                    f = File(revision=1, 
                             name=item, 
                             user_modified=user, 
                             size=WebFolder.get_file_size(user, rel_item_path),
                             hash=utils.hash.hash_file(WebFolder.get_abs_path(user, rel_item_path)))
                    f.save()
                    WebFolder.copy_file_to_repository(user, rel_item_path, WebFolder.get_repository_file_name(f.identifier, f.revision))
                    self.files.add(f)
                    item_hashs.append(f.hash)
                # file is not new
                else:
                    f = File(identifier=prev_f[0].identifier,
                             revision=prev_f[0].revision+1, 
                             name=item, 
                             user_modified=user, 
                             size=WebFolder.get_file_size(user, rel_item_path),
                             hash=utils.hash.hash_file(WebFolder.get_abs_path(user, rel_item_path)))
                    # file was modified
                    if not prev_f[0].hash == f.hash:
                        f.save()
                        WebFolder.copy_file_to_repository(user, rel_item_path, WebFolder.get_repository_file_name(f.identifier, f.revision))
                        self.files.add(f)
                        item_hashs.append(f.hash)
                    # file was not modified
                    else:
                        self.files.add(prev_f[0])
                        item_hashs.append(prev_f[0].hash)
                
            # item is a directory
            elif WebFolder.is_dir(user, rel_item_path):
                prev_d = prev_dir.sub_directories.filter(name=item)
                # directory is new
                if not prev_d:
                    d = Directory(revision=1,
                                  name=item,
                                  user_modified=user,
                                  size=WebFolder.get_dir_size(user, rel_item_path))
                    d.save()
                    self.sub_directories.add(d)
                    d.save_recursive(user, rel_item_path)
                    item_hashs.append(d.hash)
                # directory is not new
                else:
                    d = Directory(identifier=prev_d[0].identifier,
                                  revision=prev_d[0].revision+1,
                                  name=item,
                                  user_modified=user,
                                  size=WebFolder.get_dir_size(user, rel_item_path))
                    d.save()
                    d.push_recursive(user, rel_item_path, prev_d[0])
                    # directory was modified
                    if not prev_d[0].hash == d.hash:
                        self.sub_directories.add(d)
                        item_hashs.append(d.hash)
                    # directory was not modified
                    else:
                        d.delete()
                        self.sub_directories.add(prev_d[0])
                        item_hashs.append(prev_d[0].hash)
                    
        # Set directory hash
        self.hash = utils.hash.hash_dir(self.name, item_hashs)
        self.save()
                
 
    def download_recursive(self, user, rel_path, progress):
        """Download all subdirectories and files of this directory."""
        # download files
        for f in self.files.all():
            WebFolder.copy_file_to_webfolder(user, WebFolder.get_repository_file_name(f.identifier, f.revision), 
                                             os.path.join(rel_path, f.name))
            # update progress
            data = {ProgressParam.CURRENT : WebFolder.get_dir_size(user, progress.rel_path),
                    ProgressParam.TOTAL : progress.collection.directory.size,
                    ProgressParam.CURRENT_POS: os.path.join(rel_path, f.name)
                    }
            update_progress(progress.task_id, data)
            
        # download directories
        for d in self.sub_directories.all():
            rel_dir_path = os.path.join(rel_path, d.name)
            WebFolder.create_directory(user, rel_dir_path)
            d.download_recursive(user, rel_dir_path, progress)

    
    def download_recursive_public(self, rel_path, progress):
        """Download all subdirectories and files of this directory."""
        # download files
        for f in self.files.all():
            PublicFolder.copy_file_to_public_folder(PublicFolder.get_repository_file_name(f.identifier, f.revision), 
                                             os.path.join(rel_path, f.name))
            # update progress
            data = {ProgressParam.CURRENT : PublicFolder.get_dir_size(progress.rel_path),
                    ProgressParam.TOTAL : progress.collection.directory.size,
                    ProgressParam.CURRENT_POS: os.path.join(rel_path, f.name)          
                    }
            update_progress(progress.task_id, data)
        
        # download directories
        for d in self.sub_directories.all():
            rel_dir_path = os.path.join(rel_path, d.name)
            PublicFolder.create_directory(rel_dir_path)
            d.download_recursive_public(rel_dir_path, progress)
                       

    def save(self, *args, **kwargs):
        """Find max id before initial a directory and check required fields."""
        # initial directory
        if not self.id and self.revision==1:
            created = False
            while not created:
                try:
                    # raise exception if name is empty
                    if self.name=="":
                        raise IntegrityError("collection_directory.name may not be empty")  
                    # get next id for the directory and save it
                    max_id = Directory.objects.all().aggregate(models.Max('identifier'))['identifier__max']
                    max_id = 0 if not max_id else max_id
                    self.identifier = max_id + 1
                    super(Directory, self).save(*args, **kwargs)
                    created = True
                except IntegrityError as exc:
                    if self.user_modified_id==None or self.name=="" or self.size==None:
                        raise exc                   
                    else:
                        pass
        # update directory
        else:
            # raise exception if name is empty
            if self.name=="":
                raise IntegrityError("collection_directory.name may not be empty")  
            else:
                super(Directory, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'ID: %d | Revision: %d | Name: %s' % (self.identifier, 
                                                      self.revision, 
                                                      self.name)              
     
    class Meta:
        unique_together = (("identifier", "revision"),)
        verbose_name = "directory"
        verbose_name_plural = "directories"

   

class File(models.Model):
    """The File model represent a file of a collection. It will be
    placed in any directory."""
    
    identifier = models.IntegerField(verbose_name=u'ID')
    revision = models.IntegerField(verbose_name=u'revision', default=1)
    name = models.CharField(verbose_name=u'name', max_length=120)
     
    user_modified = models.ForeignKey('authentication.User', 
                                      verbose_name=u'user who modified',
                                      related_name='file_modified')
    date_modified = models.DateTimeField(verbose_name=u'last modified', auto_now_add=True)
    
    size = models.BigIntegerField(verbose_name=u'size')
    
    hash = models.CharField(verbose_name=u'hash', max_length=64)
    
    def save(self, *args, **kwargs):
        """Find max id before initial a directory and check required fields."""    
        # initial file
        if not self.id and self.revision==1:
            created = False
            while not created:
                try:
                    # raise exception if name is empty
                    if self.name=="":
                        raise IntegrityError("collection_file.name may not be empty")  
                    # get next id for the directory and save it
                    max_id = File.objects.all().aggregate(models.Max('identifier'))['identifier__max']
                    max_id = 0 if not max_id else max_id
                    self.identifier = max_id + 1
                    super(File, self).save(*args, **kwargs)
                    created = True
                except IntegrityError as exc:
                    if self.user_modified_id==None or self.name=="" or self.size==None:
                        raise exc                   
                    else:
                        pass        
        # update directory
        else:
            # raise exception if name is empty
            if self.name=="":
                raise IntegrityError("collection_directory.name may not be empty")  
            else:
                super(File, self).save(*args, **kwargs)
      
    def __unicode__(self):
        return 'ID: %d | Revision: %d | Name: %s' % (self.identifier, 
                                                      self.revision, 
                                                      self.name)
        
    class Meta:
        unique_together = (("identifier", "revision"),)
        verbose_name = "file"
        verbose_name_plural = "files"
 
 
class Tag(models.Model):
    """The Tag model contains a key-value pair to support the search
    process of a collection."""
    
    key = models.CharField(verbose_name=u'Key',
                           choices=enum.Tag.CHOICES_A,
                           default=enum.Tag.TITLE,
                           max_length=128)
    value = models.CharField(verbose_name=u'Value', max_length=256)
     
    def __unicode__(self):
        return 'Key: %s | Value: %s' % (self.key, self.value)
    
    class Meta:
        unique_together = (("key", "value"),)
        verbose_name = "tag"
        verbose_name_plural = "tags"
        

from subprocess import Popen, PIPE, STDOUT

class WebFolder():
    """Represent the webfolder of each user."""
    
    traits_parser = ConfigParser.RawConfigParser()
    
    
    @staticmethod
    def get_abs_path(user, rel_path):
        return os.path.join(WEBDAV_DIR, user.user_name, utils.path.no_slash(rel_path))
    
    
    @staticmethod
    def list_dir(user, rel_path):
        return os.listdir(WebFolder.get_abs_path(user, rel_path))
    
    
    @staticmethod
    def is_file(user, rel_path):
        return os.path.isfile(WebFolder.get_abs_path(user, rel_path))
    
    
    @staticmethod
    def is_dir(user, rel_path):
        return os.path.isdir(WebFolder.get_abs_path(user, rel_path))
    
    
    @staticmethod
    def get_file_size(user, rel_path):
        return os.path.getsize(WebFolder.get_abs_path(user, rel_path))
    
    
    @staticmethod
    def get_dir_size(user, rel_path):
        total_size = 0#get_file_size(user, rel_path)
        for item in WebFolder.list_dir(user, rel_path):
            rel_item_path = os.path.join(rel_path, item)
            if WebFolder.is_file(user, rel_item_path):
                total_size += WebFolder.get_file_size(user, rel_item_path)
            elif WebFolder.is_dir(user, rel_item_path):
                total_size += WebFolder.get_dir_size(user, rel_item_path)
        return total_size
    
    
    @staticmethod
    def remove_dir_recursive(user, rel_path):
        abs_path = WebFolder.get_abs_path(user, rel_path)
        if os.path.exists(abs_path):
            shutil.rmtree(abs_path)
    
    
    @staticmethod
    def get_repository_file_name(file_id, file_rev):
        return str(file_id) + "-" + str(file_rev) 
    
    
    @staticmethod
    def copy_file_to_repository(user, rel_src_path, dst_name):
        abs_src_path = WebFolder.get_abs_path(user, rel_src_path)
        shutil.copy(abs_src_path, os.path.join(REPOSITORY_DIR, dst_name))
    
        
    @staticmethod
    def copy_file_to_webfolder(user, src_name, rel_dst_path):
        abs_dst_path = WebFolder.get_abs_path(user, rel_dst_path)
        shutil.copy(os.path.join(REPOSITORY_DIR, src_name), abs_dst_path)
    
        
    @staticmethod
    def create_directory(user, rel_path):
        abs_path = WebFolder.get_abs_path(user, rel_path)
        os.makedirs(abs_path)
    
    
    @staticmethod
    def is_collection(user, rel_path):
        abs_path = WebFolder.get_abs_path(user, rel_path)
        if(os.path.exists(os.path.join(abs_path, COLLECTION_INFO_DIR, COLLECTION_DESCRIPTION_FILE)) and
           os.path.exists(os.path.join(abs_path, COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE))):
            WebFolder.traits_parser.read(os.path.join(abs_path, COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE))
            return bool(user.subscriptions.filter(identifier=WebFolder.traits_parser.get('Common', 'id')))
        else:
            return False
        
    
    @staticmethod
    def get_collection_of_item(user, rel_path):
        rel_path = utils.path.no_slash(rel_path)
        abs_path = WebFolder.get_abs_path(user, rel_path)
        if (rel_path=="" or not os.path.exists(abs_path)):
            return None
        elif WebFolder.is_collection(user, rel_path):
            WebFolder.traits_parser.read(os.path.join(abs_path, COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE))
            return user.subscriptions.get(identifier=WebFolder.traits_parser.get('Common', 'id'))
        else:
            return WebFolder.get_collection_of_item(user, os.path.split(rel_path)[0])
    
    
    @staticmethod
    def get_collection(user, rel_path):
        if WebFolder.is_collection(user, rel_path):
            WebFolder.traits_parser.read(os.path.join(WebFolder.get_abs_path(user, rel_path), COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE))
            return user.subscriptions.get(identifier=WebFolder.traits_parser.get('Common', 'id'))
        else:
            return None 
        
    
    @staticmethod
    def get_dir(user, rel_path):
        collection = WebFolder.get_collection_of_item(user, rel_path)
        if(collection):
            d = collection.get_dir(rel_path)
            if(d):
                return d
            else:
                return None
        else:
            return None
    
    
    @staticmethod
    def get_file(user, rel_path):
        collection = WebFolder.get_collection_of_item(user, rel_path)
        if(collection):
            f = collection.get_file(rel_path)
            if(f):
                return f
            else:
                return None
        else:
            return None
        
    
    @staticmethod
    def create_owncloud_dir(user):
        WebFolder.create_directory(user, OWNCLOUD_DIR_NAME)
        
        
    @staticmethod
    def is_mounted(user):
        return os.path.ismount(WebFolder.get_abs_path(user, OWNCLOUD_DIR_NAME))
        

    @staticmethod
    def mount_owncloud(user, owncloud_user, owncloud_password):
        cmd = os.path.join(BASH_DIR, "mount_owncloud.sh") + " " + owncloud_user + " " + owncloud_password + " " + WebFolder.get_abs_path(user, OWNCLOUD_DIR_NAME)
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        error = p.stderr.read()
        logger.error("Mount ownCloud in webfolder " + user.user_name + ": " + error)
        return WebFolder.is_mounted(user)
    
    
    @staticmethod
    def unmount_owncloud(user):
        cmd = os.path.join(BASH_DIR, "unmount_owncloud.sh") + " "  + WebFolder.get_abs_path(user, OWNCLOUD_DIR_NAME)
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        error = p.stderr.read()
        logger.error("Unmount ownCloud in webfolder " + user.user_name + ": " + error)
        return not WebFolder.is_mounted(user)
    
    
class PublicFolder():
    """Represent the public folder."""
    
    traits_parser = ConfigParser.RawConfigParser()
        
        
    @staticmethod
    def get_abs_path(rel_path):
        return os.path.join(WEBDAV_DIR, PUBLIC_USER, utils.path.no_slash(rel_path))

    
    @staticmethod
    def list_dir(rel_path):
        return os.listdir(PublicFolder.get_abs_path(rel_path))
    
    
    @staticmethod
    def is_file(rel_path):
        return os.path.isfile(PublicFolder.get_abs_path(rel_path))
    
    
    @staticmethod
    def is_dir(rel_path):
        return os.path.isdir(PublicFolder.get_abs_path(rel_path))
    
    
    @staticmethod
    def get_file_size(rel_path):
        return os.path.getsize(PublicFolder.get_abs_path(rel_path))

    
    @staticmethod
    def get_dir_size(rel_path):
        total_size = 0#get_file_size(rel_path)
        for item in PublicFolder.list_dir(rel_path):
            rel_item_path = os.path.join(rel_path, item)
            if PublicFolder.is_file(rel_item_path):
                total_size += PublicFolder.get_file_size(rel_item_path)
            elif PublicFolder.is_dir(rel_item_path):
                total_size += PublicFolder.get_dir_size(rel_item_path)
        return total_size
    
    
    @staticmethod
    def remove_dir_recursive(rel_path):
        abs_path = PublicFolder.get_abs_path(rel_path)
        if os.path.exists(abs_path):
            shutil.rmtree(abs_path)
            
    
    @staticmethod
    def get_repository_file_name(file_id, file_rev):
        return str(file_id) + "-" + str(file_rev) 
    
        
    @staticmethod
    def copy_file_to_public_folder(src_name, rel_dst_path):
        abs_dst_path = PublicFolder.get_abs_path(rel_dst_path)
        shutil.copy(os.path.join(REPOSITORY_DIR, src_name), abs_dst_path)


    @staticmethod
    def create_directory(rel_path):
        abs_path = PublicFolder.get_abs_path(rel_path)
        os.makedirs(abs_path)
        
    
    @staticmethod
    def is_collection(rel_path):
        abs_path = PublicFolder.get_abs_path(rel_path)
        if(os.path.exists(os.path.join(abs_path, COLLECTION_INFO_DIR, COLLECTION_DESCRIPTION_FILE)) and
           os.path.exists(os.path.join(abs_path, COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE))):
            PublicFolder.traits_parser.read(os.path.join(abs_path, COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE))
            return bool(Collection.objects.get(identifier=PublicFolder.traits_parser.get('Common', 'id'),
                                               revision=PublicFolder.traits_parser.get('Common', 'revision')))
        else:
            return False
    
    
    @staticmethod
    def get_collection_of_item(rel_path):
        rel_path = utils.path.no_slash(rel_path)
        abs_path = PublicFolder.get_abs_path(rel_path)
        if (rel_path=="" or not os.path.exists(abs_path)):
            return None
        elif PublicFolder.is_collection(rel_path):
            PublicFolder.traits_parser.read(os.path.join(abs_path, COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE))
            return Collection.objects.get(identifier=PublicFolder.traits_parser.get('Common', 'id'),
                                          revision=PublicFolder.traits_parser.get('Common', 'revision'))
        else:
            return PublicFolder.get_collection_of_item(os.path.split(rel_path)[0])
        
    @staticmethod
    def get_collection(rel_path):
        if PublicFolder.is_collection(rel_path):
            PublicFolder.traits_parser.read(os.path.join(PublicFolder.get_abs_path(rel_path), COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE))
            return Collection.objects.get(identifier=PublicFolder.traits_parser.get('Common', 'id'),
                                          revision=PublicFolder.traits_parser.get('Common', 'revision'))
        else:
            return None 
        
    
    @staticmethod
    def get_dir(rel_path):
        collection = PublicFolder.get_collection_of_item(rel_path)
        if(collection):
            d = collection.get_dir(rel_path)
            if(d):
                return d
            else:
                return None
        else:
            return None
    
    
    @staticmethod
    def get_file(rel_path):
        collection = PublicFolder.get_collection_of_item(rel_path)
        if(collection):
            f = collection.get_file(rel_path)
            if(f):
                return f
            else:
                return None
        else:
            return None
        
    
