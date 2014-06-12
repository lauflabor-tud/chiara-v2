from django.contrib import admin
from .models import Collection, Directory, File, Tag


class CollectionAdmin(admin.ModelAdmin):
    """The CollectionAdmin is responsible for the look and feel of
    the collection admin window."""
    
    filter_horizontal = ('tags',)



class DirectoryAdmin(admin.ModelAdmin):
    """The DirectoryAdmin is responsible for the look and feel of
    the directory admin window."""

    filter_horizontal = ('files', 'sub_directories')




# Register all modules
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Directory, DirectoryAdmin)
admin.site.register(File)
admin.site.register(Tag)
