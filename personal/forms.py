# -*- coding: utf-8 -*-
from django import forms
import datetime
from personal.models import UserData, PaidService

base_services = PaidService.objects.filter(name__startswith='base_')
PAYMENT_PURPOSES = []
for base in base_services:
    PAYMENT_PURPOSES.append((u'ОПЛАТА ДОСТУПА К БАЗЕ %s' % base.ru_name, u'База %s' % base.ru_name))
PAYMENT_PURPOSES.append((u'ОПЛАТА НА ЛИЧНЫЙ СЧЕТ ЦЕНТРИНФОРМ', u'Личный счет ЦентрИнформ'))
PAYMENT_CASES = ((u'На карту ПриватБанка', u'На карту ПриватБанка'),
                 (u'На счет ПриватБанка', u'На счет ПриватБанка'),
                 (u'I-Box, Alfa-Pay, Qiwi', u'I-Box, Alfa-Pay, Qiwi'),
                 (u'Webmoney', u'Webmoney'),
                 (u'Через кассу по квитанции', u'Через кассу по квитанции'),
                 (u'На счет для юр. лиц', u'На счет для юр. лиц'))

class PaymentReportForm(forms.Form):
    def __init__(self, *args, **kwargs):
        req = kwargs.pop('req', None)
        super(PaymentReportForm, self).__init__(*args, **kwargs)
        if req and req.user.is_authenticated():
            self.fields['username'].initial = req.user.username
            self.fields['user_email'].initial = req.user.email
            self.fields['fio_company'].initial = req.user.get_full_name()
        
    payment_purpose = forms.CharField(max_length=40, 
                                      widget=forms.Select(choices=PAYMENT_PURPOSES))
    payment_case = forms.CharField(max_length=40, 
                                   widget=forms.Select(choices=PAYMENT_CASES))
    check_code = forms.CharField(max_length=20)
    fio_company = forms.CharField(max_length=50)
    username = forms.CharField(max_length=30)
    user_email = forms.EmailField(max_length=30)
    user_phone = forms.CharField(max_length=20)
    sum_of_payment = forms.CharField(max_length=20)
    date_of_payment = forms.CharField(max_length=20)
    
    def get_context_data(self, *args, **kwargs):
        context = super(forms.Form, self).get_context_data(*args, **kwargs)
        
    