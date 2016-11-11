from django.contrib import admin
from personal.models import UserPayment, UserOperation, UserIP, UserMessage
from personal.models import ServicePrice

# Register your models here.
class UserPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'description', 'amount', 'pay_way', 'status')
    readonly_fields = ('user', 'advert')
    search_fields = ['user__username']
    list_filter = ['date', 'status']
    ordering = ['date']
    radio_fields = {'user': admin.VERTICAL}


class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('name','sender')


class ServicePriceAdmin(admin.ModelAdmin):
    list_display = ('kind', 'title', 'price', 'days')
    readonly_fields = ('kind',)


class UserOperationAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'service', 'advert_id', 'execution_date', 'expiration_date')
    readonly_fields = ('advert',)
    search_fields = ['user__username', 'advert__id']
    list_filter = ['service']

    def advert_id(self, obj):
        return obj.advert_id


admin.site.register(UserMessage, UserMessageAdmin)
admin.site.register(UserPayment, UserPaymentAdmin)
admin.site.register(UserIP)
admin.site.register(ServicePrice, ServicePriceAdmin)
admin.site.register(UserOperation, UserOperationAdmin)