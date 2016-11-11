from django.contrib import admin
from lesnoe.models import PageText

class PageTextAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(PageText, PageTextAdmin)