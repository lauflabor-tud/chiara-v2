import os
from chiara.settings.common import SITE_ROOT
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
    # Administration
    url(r'^admin/', include(admin.site.urls)),
    
    # Index
    url(r'^$', 'collection.views.index'),
    
    # Authentication
    url(r'^account/', 'authentication.views.my_account', name='my_account'),
    url(r'^login/$', 'authentication.views.login', name='login'),
    url(r'^logout/$', 'authentication.views.logout', name='logout'),
    
    # News
    url(r'^news/', 'collection.views.news', name='news'),
    
    # My shared folder
    url(r'^shared-folder/', 'collection.views.my_shared_folder', name='my_shared_folder'),
    
    # Retrieve new collections
    url(r'^retrieve/', 'collection.views.retrieve_new_collections', name='retrieve_new_collections'),
    
    # Manage my collections
    url(r'^manage/', 'collection.views.manage_my_collections', name='manage_my_collections'),
    
    # Documentation
    url(r'^doc/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root':os.path.join(SITE_ROOT, 'documentation/build/html')}),
)
