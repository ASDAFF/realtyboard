from django.contrib import admin
from news.models import News, BlackList

class NewsAdmin(admin.ModelAdmin):
    pass
class BlackListAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'city']
    list_filter = ['city']
    search_fields = ['id', 'text']

admin.site.register(News, NewsAdmin)
admin.site.register(BlackList, BlackListAdmin)