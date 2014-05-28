from django.db import models, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
import os, utils.path
from authentication.models import UserPermission, Subscription
from utils.enums import Permission
from collection import info, webfolder

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
    
    summary = models.TextField(verbose_name=u'summary', blank=True)
    details = models.TextField(verbose_name=u'details', blank=True)
    authors = models.ManyToManyField('authentication.User', 
                                     verbose_name=u'authors', 
                                     related_name='author_of', 
                                     blank=True)
    comment = models.TextField(verbose_name=u'comment', blank=True)
    
    tags = models.ManyToManyField('collection.Tag', 
                                  verbose_name=u'tags',
                                  related_name='collections',
                                  blank=True) 
    
    def get_name(self):
        """Returns the name of this collection."""
        return self.directory.name
    
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
            # check if directoy exists
            if(sub_dir):
                sub_dir = sub_dir[0]
            else:
                return None
        return sub_dir
    
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
        
        # Set collection attributes
        self.directory = root_dir
        self.revision = 1
        self.save()
        self.summary = desc_parser.get_summary()
        self.details = desc_parser.get_details()
        self.comment = "Add the collection to the repository."
        self.save()
        for (key,value) in desc_parser.get_tags():
            tag = Tag(key=key, value=value)
            tag.save()
            self.tags.add(tag)
    
        # Set user access
        permission = UserPermission(collection=self,
                                    user=user,
                                    permission=Permission.WRITE)
        permission.save()
        self.authors.add(user)
        
        # Set user subscription
        subscription = Subscription(collection=self,
                                    user=user)
        subscription.save()

    
    def push_local_revision(self, user, rel_path):
        pass
    
    
    def download(self, user, rel_path):
        pass
    

    def unsubscribe(self, user):
        """Unsubscribe the collection of the user."""
        try:
            subscription = Subscription.objects.get(user=user, collection=self)
            subscription.delete()
        except ObjectDoesNotExist:
            pass


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
    date_created = models.DateField(verbose_name=u'creation date', 
                                    auto_now_add=True, 
                                    editable=False)
    date_modified = models.DateField(verbose_name=u'last modified', auto_now_add=True)
     
    size = models.BigIntegerField(verbose_name=u'size')
 
    def is_root(self):
        """Check if this directory is the root directory."""
        return len(self.parent_directory.all())==0
        
    def save_recursive(self, user, rel_path):
        """Save all subdirectories and files of this directory and 
        create connections to this directory."""
        for item in webfolder.list_dir(user, rel_path):
            rel_item_path = os.path.join(rel_path, item)
            if webfolder.is_file(user, rel_item_path):                
                f = File(revision=1, 
                         name=item, 
                         user_modified=user, 
                         size=webfolder.get_file_size(user, rel_item_path))
                f.save()
                webfolder.add_file_to_repository(user, rel_item_path, webfolder.get_repository_file_name(f.identifier, f.revision))
                self.files.add(f)
            elif webfolder.is_dir(user, rel_item_path):
                d = Directory(revision=1,
                              name=item,
                              user_modified=user,
                              size=webfolder.get_dir_size(user, rel_item_path))
                d.save()
                self.sub_directories.add(d)
                d.save_recursive(user, rel_item_path)

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
    date_created = models.DateField(verbose_name=u'creation date', 
                                    auto_now_add=True, 
                                    editable=False)
    date_modified = models.DateField(verbose_name=u'last modified', auto_now_add=True)
     
    size = models.BigIntegerField(verbose_name=u'size')
    
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
    
    key = models.CharField(verbose_name=u'Key', max_length=120)
    value = models.CharField(verbose_name=u'Value', max_length=120)
     
    def __unicode__(self):
        return 'Key: %s | Value: %s' % (self.key, self.value)
    
    class Meta:
        verbose_name = "tag"
        verbose_name_plural = "tags"

