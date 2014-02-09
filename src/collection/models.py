from django.db import models
    
    
class Collection(models.Model):
    """The Collection model represent a collection of directories
    and files. It contains a root directory with the name, revision
    and further information."""

    identifier = models.IntegerField(verbose_name=u'ID')
    revision = models.IntegerField(verbose_name=u'revision', default=1)

    directory = models.OneToOneField('collection.Directory', 
                                     related_name='collection',
                                     primary_key=True)
    
    summary = models.TextField(verbose_name=u'summary', blank=True)
    description = models.TextField(verbose_name=u'description', blank=True)
    authors = models.ManyToManyField('authentication.User', 
                                     verbose_name=u'authors', 
                                     related_name='author_of')
    
    tags = models.ManyToManyField('collection.Tag', 
                                  blank=True, 
                                  verbose_name=u'tags',
                                  related_name='collections')
    
    def get_identifier(self):
        return self.directory.identifier
    
    def get_revision(self):
        return self.directory.revision
    
    def get_name(self):
        return self.directory.name
    
    def __unicode__(self):
        return unicode(self.directory)
        
    class Meta:
        verbose_name = "collection"
        verbose_name_plural = "collections"



class Directory(models.Model):
    """The Directory model represent a directory of a collection.
    The root directory is the primary key of a collection."""

    identifier = models.IntegerField(verbose_name=u'ID')
    revision = models.IntegerField(verbose_name=u'revision', default=1)
    name = models.CharField(verbose_name=u'name', max_length=120)
    
    sub_directories = models.ManyToManyField('collection.Directory', 
                                             blank=True,
                                             verbose_name=u'sub directories',
                                             related_name='parent_directories')
    files = models.ManyToManyField('collection.File', 
                                   blank=True,
                                   verbose_name=u'files',
                                   related_name='parent_directories')

    user_modified = models.ForeignKey('authentication.User', 
                                      verbose_name=u'user who modified',
                                      related_name='directory_modified')
    date_created = models.DateField(verbose_name=u'creation date', 
                                    auto_now_add=True, 
                                    editable=False)
    date_modified = models.DateField(verbose_name=u'last modified', auto_now_add=True)
     
    size = models.BigIntegerField(verbose_name=u'size')
 
    def is_root(self):
        return len(self.parent_directory.all())==0
        
    def __unicode__(self):
        return 'ID: %d | Revision: %d | Name: %s)' % (self.identifier, 
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
 
    def __unicode__(self):
        return 'ID: %d | Revision: %d | Name: %s)' % (self.identifier, 
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

