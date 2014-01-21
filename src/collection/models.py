from django.db import models
    
    
class Collection(models.Model):
    """ Collection model. """

    cid = models.IntegerField()
    revision = models.IntegerField(default=1)
    name = models.CharField(u'Name', max_length=100)
 
    class Meta:
        unique_together = (('cid', 'revision'),)
 
    def __unicode__(self):
        return '%s (rev. %d)' % (self.name, self.revision)



class CollectionRelation(models.Model):

    cid = models.IntegerField()
    revision = models.IntegerField()
    parent_cid = models.IntegerField()
    parent_revision = models.IntegerField()

    def __unicode__(self):
        return 'collection: %d (rev. %d), parent: %d (rev. %d)' % (self.cid, self.revision, self.parent_cid, self.parent_revision)



class File(models.Model):

    fid = models.IntegerField()
    revision = models.IntegerField(default=1)
    name = models.CharField(u'Name', max_length=100)

    class Meta:
        unique_together = (("fid", "revision"),)

    def __unicode__(self):
        return '%s (rev. %d)' % (self.name, self.revision)



class FileRelation(models.Model):

    fid = models.IntegerField()
    revision = models.IntegerField()
    cid = models.IntegerField()
    crevision = models.IntegerField(default=1)

    def __unicode__(self):
        return 'file: %d (rev. %d), collection: %d (rev. %d)' % (self.fid, self.revision, self.cid, self.crevision)



class Tag(models.Model):

    key = models.CharField(u'Key', max_length=100)
    value = models.CharField(u'Value', max_length=100)
    
    def __unicode__(self):
        return 'key: %s, value: %s' % (self.key, self.value)

    
    
    