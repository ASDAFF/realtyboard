from django.contrib import admin
from lukomorye.models import GallaryModel, SiteText

# Register your models here.
class GallaryModelAdmin(admin.ModelAdmin):
   pass 
   
   
class SiteTextAdmin(admin.ModelAdmin):
    pass
    
    
admin.site.register(GallaryModel, GallaryModelAdmin)
admin.site.register(SiteText, SiteTextAdmin)