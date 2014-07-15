from django.db import models

class News(models.Model):
    """The News model contains all news messages."""
    
    date = models.DateTimeField(verbose_name=u'date', auto_now_add=True)
    user = models.ForeignKey('authentication.User', 
                             verbose_name=u'user',
                             related_name='news_log')
    content = models.TextField(verbose_name=u'content', blank=True)
    collection = models.ForeignKey('collection.Collection',
                                   verbose_name=u'collection',
                                   related_name='news_log',
                                   blank=True,
                                   null=True)
    group = models.ForeignKey('authentication.Group',
                              verbose_name=u'group',
                              related_name='news_log',
                              blank=True,
                              null=True)

    def __unicode__(self):
        return 'Date: %s | User: %s | Content: %s' % (self.date, self.user.user_name, self.content)
    
    class Meta:
        verbose_name = "news"
        verbose_name_plural = "news"