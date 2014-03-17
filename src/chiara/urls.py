import os
from chiara.settings.common import SITE_ROOT
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'chiara.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', 'collection.views.index'),
    
    url(r'^your_account/', 'authentication.views.your_account'),
    
    url(r'^news/', 'collection.views.news'),
    url(r'^my_shared_folder/', 'collection.views.my_shared_folder'),
    url(r'^retrieve_new_collections/', 'collection.views.retrieve_new_collections'),
    url(r'^manage_my_collections/', 'collection.views.manage_my_collections'),
    
    url(r'^documentation/(?P<path>.*)$', 'django.views.static.serve', \
        {'document_root':os.path.join(SITE_ROOT, 'documentation/build/html')}),
)
