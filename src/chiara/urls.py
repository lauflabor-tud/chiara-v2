import os
from chiara.settings.common import SRC_DIR
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import password_reset
admin.autodiscover()

urlpatterns = patterns('',
    
    # Administration
    url(r'^admin/', include(admin.site.urls)),
    
    # Index
    url(r'^$', 'collection.views.index'),
    
    # Authentication
    url(r'^preferences/$', 'authentication.views.preferences', name='preferences'),
    url(r'^preferences/change-password/$', 'authentication.views.password_change', name='password_change'),
    url(r'^preferences/change-password/done/$', 'authentication.views.password_change_done', name='password_change_done'),
    url(r'^login/$', 'authentication.views.login', name='login'),
    url(r'^logout/$', 'authentication.views.logout', name='logout'),
    
    
    # News
    url(r'^news/', 'log.views.news', name='news'),
    
    # Public folder
    url(r'^public-folder/$', 'collection.views.public_folder', name='public_folder'),
    url(r'^public-folder/(?P<rel_path>.*)/$', 'collection.views.public_folder', name='public_folder'),

    # My shared folder
    url(r'^shared-folder/$', 'collection.views.my_shared_folder', name='my_shared_folder'),
    url(r'^shared-folder/(?P<rel_path>.*)/$', 'collection.views.my_shared_folder', name='my_shared_folder'),
    url(r'^operations/$', 'collection.views.operations', name='operations'),
    url(r'^download_to_disk/(?P<rel_file_path>.*)/$', 'collection.views.download_to_disk', name='download_to_disk'),
    url(r'^mount-owncloud/$', 'collection.views.mount_owncloud', name='mount_owncloud'),
    
    # Retrieve new collections
    url(r'^retrieve/', 'collection.views.retrieve_new_collections', name='retrieve_new_collections'),
    
    # Manage my collections
    url(r'^manage/', 'collection.views.manage_my_collections', name='manage_my_collections'),
    
    # Documentation
    url(r'^doc/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root':os.path.join(SRC_DIR, 'documentation/build/html')}),
)
