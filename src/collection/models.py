from __future__ import division
from django.db import models, IntegrityError
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist
import os, utils.path, utils.hash, re, sys, datetime
from authentication.models import UserPermission, GroupPermission, Subscription
from utils import enum
import utils.date
from collection import info, webfolder
from exception.exceptions import *


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
    
    def get_user_permission(self, user):
        return user.userpermission_set.get(collection=self).permission
    
    @staticmethod
    def retrieve_collections(user, tags):
        """Search the collections in the repository by filtering with the given tags 
        and permissions of the user."""
        # get all collections in newest revision which the user is permitted
        permitted_collections = [c for c in user.permissions.all() if c==c.get_revision(sys.maxint)]
        # remove all subscribed collections
        subsribed_collections = [c for c in user.subscriptions.all() 
                                 if c.revision==c.get_all_revisions().aggregate(Max('revision'))['revision__max']]
        collections = list(set(permitted_collections)-set(subsribed_collections))
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
                             size=webfolder.get_dir_size(user, rel_path))
        root_dir.save()
        info.create_traits(user, rel_path, root_dir.identifier)
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
                                 size=webfolder.get_dir_size(user, rel_path))
            root_dir.save()
            info.create_traits(user, rel_path, root_dir.identifier)
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
        # collection is not at newest revision
        else:
            raise NotNewestRevisionException()
        
            
    def download(self, user, rel_path):
        """Download the collection into the given directory of the user's webfolder."""
        # copy files into the webfolder
        rel_dir_path = os.path.join(rel_path, self.directory.name)
        webfolder.remove_dir_recursive(user, rel_dir_path)
        webfolder.create_directory(user, rel_dir_path)
        self.directory.download_recursive(user, rel_dir_path)
        # Set user subscription
        subscription = Subscription(collection=self,
                                    user=user)
        subscription.save()
    

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
        return len(self.parent_directory.all())==0
 
        
    def save_recursive(self, user, rel_path):
        """Save all subdirectories and files of this directory and 
        create connections to this directory."""
        item_hashs = []
        # Save recursive files and directories
        for item in webfolder.list_dir(user, rel_path):
            rel_item_path = os.path.join(rel_path, item)
            if webfolder.is_file(user, rel_item_path):                
                f = File(revision=1, 
                         name=item, 
                         user_modified=user, 
                         size=webfolder.get_file_size(user, rel_item_path),
                         hash=utils.hash.hash_file(webfolder.get_abs_path(user, rel_item_path))
                         )
                f.save()
                webfolder.copy_file_to_repository(user, rel_item_path, webfolder.get_repository_file_name(f.identifier, f.revision))
                self.files.add(f)
                item_hashs.append(f.hash)
            elif webfolder.is_dir(user, rel_item_path):
                d = Directory(revision=1,
                              name=item,
                              user_modified=user,
                              size=webfolder.get_dir_size(user, rel_item_path))
                
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
        
        for item in webfolder.list_dir(user, rel_path):
            rel_item_path = os.path.join(rel_path, item)
            # item is a file
            if webfolder.is_file(user, rel_item_path):
                prev_f = prev_dir.files.filter(name=item)
                # file is new
                if not prev_f:
                    f = File(revision=1, 
                             name=item, 
                             user_modified=user, 
                             size=webfolder.get_file_size(user, rel_item_path),
                             hash=utils.hash.hash_file(webfolder.get_abs_path(user, rel_item_path)))
                    f.save()
                    webfolder.copy_file_to_repository(user, rel_item_path, webfolder.get_repository_file_name(f.identifier, f.revision))
                    self.files.add(f)
                    item_hashs.append(f.hash)
                # file is not new
                else:
                    f = File(identifier=prev_f[0].identifier,
                             revision=prev_f[0].revision+1, 
                             name=item, 
                             user_modified=user, 
                             size=webfolder.get_file_size(user, rel_item_path),
                             hash=utils.hash.hash_file(webfolder.get_abs_path(user, rel_item_path)))
                    # file was modified
                    if not prev_f[0].hash == f.hash:
                        f.save()
                        webfolder.copy_file_to_repository(user, rel_item_path, webfolder.get_repository_file_name(f.identifier, f.revision))
                        self.files.add(f)
                        item_hashs.append(f.hash)
                    # file was not modified
                    else:
                        self.files.add(prev_f[0])
                        item_hashs.append(prev_f[0].hash)
                
            # item is a directory
            elif webfolder.is_dir(user, rel_item_path):
                prev_d = prev_dir.sub_directories.filter(name=item)
                # directory is new
                if not prev_d:
                    d = Directory(revision=1,
                                  name=item,
                                  user_modified=user,
                                  size=webfolder.get_dir_size(user, rel_item_path))
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
                                  size=webfolder.get_dir_size(user, rel_item_path))
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
                
 
    def download_recursive(self, user, rel_path):
        """Download all subdirectories and files of this directory."""
        # download files
        for f in self.files.all():
            webfolder.copy_file_to_webfolder(user, webfolder.get_repository_file_name(f.identifier, f.revision), 
                                             os.path.join(rel_path, f.name))
        # download directories
        for d in self.sub_directories.all():
            rel_dir_path = os.path.join(rel_path, d.name)
            webfolder.create_directory(user, rel_dir_path)
            d.download_recursive(user, rel_dir_path)
                       

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

