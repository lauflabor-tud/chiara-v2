from django.contrib import admin
from .models import News

class NewsAdmin(admin.ModelAdmin):
    """The CollectionAdmin is responsible for the look and feel of
    the collection admin window."""
    
    list_display = ('date', 'user', 'content',)
    list_filter = ('date',)

# Register all modules
admin.site.register(News, NewsAdmin)