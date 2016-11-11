# -*- coding: utf-8 -*-
from board.models import CURRENCY_CHOICES
from django import forms
from django.forms import widgets, MultiWidget
import pickle

class MultiWidgetBasic(forms.widgets.MultiWidget):
    # price = 0
    # currency = "ГРН"

    # def value_from_datadict(self, data, files, name):
    #     print data
    #     self.price = data['price']
    #     self.currency = data['currency']
    #     print self.price
    #     return super(MultiWidgetBasic, self).value_from_datadict(data, files, 
    #                                                                 name)

    def __init__(self, attrs=None):
        widgets = [forms.TextInput(),
                   forms.Select(choices=CURRENCY_CHOICES),]
        super(MultiWidgetBasic, self).__init__(widgets, attrs)
 
    def decompress(self, value):
        import pdb;pdb.set_trace()
        if value:
            price, currency = value.split(" ")
            return [price, currency]
        else:
            return ['0', '0']
 
 
class MultiExampleField(forms.fields.MultiValueField):
    widget = MultiWidgetBasic
 
    def __init__(self, *args, **kwargs):        
        
        list_fields = [forms.fields.CharField(max_length=31),
                       forms.fields.CharField(max_length=31)]
        super(MultiExampleField, self).__init__(list_fields, *args, **kwargs)
        self.label = u'Цена'
 
    def compress(self, values):
        ## compress list to single object                                               
        ## eg. date() >> u'31/12/2012'                                                  
        print values
        print "############################"
        return values[0]

    def to_python(self, value):
        print "############################"
        print value
        try:
            return value[0]  # , 'currency': value[1]}
        except ValueError:
            raise forms.ValidationError(_(u'Wrong Price'))    


class MyTestField(forms.CharField):
    def formfield(self, **kwargs):
        return super(MyTestField, self).formfield(form_class=MultiExampleField)            