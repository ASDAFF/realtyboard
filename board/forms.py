# encoding: utf-8
import logging
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.forms.fields import *
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField, model_to_dict, CheckboxSelectMultiple
from django.forms.widgets import Select
from django.forms.widgets import *
from django.utils.safestring import mark_safe
from widgets import MyTestField


from board.models import *
from personal.models import UserData

# Get an instance of a logger
logger = logging.getLogger()

CHECKBOX_CHOICES = (('1', '1'),
                    ('2', '2'),
                    ('3', '3'),
                    ('4', '4'),
                    ('5', '5+'))
SELECT_LEVEL = (('1', 'по убыванию'),
                ('2', 'по возрастанию'))
SELECT_OBJ = (('date_of_update', 'по дате'),
              ('price_uah', 'по цене'))
OBJ_ALL = (('kvartiru', 'Квартиру'),
           ('gostinku-komnatu', 'Комнату'),
           ('dom', 'Дом'),
           ('uchastok', 'Участок'),
           ('kommercheskuyu-nedvizhimost', 'Нежилой фонд'))
SHOW_NOTE_CHOICES = ((0, u'Показывать все'),
                     (1, u'Показать только'),
                     (2, u'Не показывать'))
PRO_COLORS = ((u'green', mark_safe(u'Отмеченные <span class="green">зеленым</span>')),
              (u'blue', mark_safe(u'Отмеченные <span class="blue">синим</span>')),
              (u'red', mark_safe(u'Отмеченные <span class="red">красным</span>')),
              (u'yellow', mark_safe(u'Отмеченные <span class="yellow">желтым</span>')))
                # (('with-comment', u'С комментариями'),
                # ('all-marked', u'Все выделенные'),

#snimu-dom
#snimu-komnatu
#snimu-gostinku-komnatu
#snimu-kvartiru
#snimu-zemelnyij-uchastok
#snimu-kommercheskuyu-nedvizhimost
ACT = (('prodam', 'Купить'),
       ('sdam', 'Снять'),
       ('kuplyu', 'Продать'),
       ('snimu', 'Сдать'),)
TERM_LIST = (("0", u"Все время"), ("1", u"Сегодня"), ("3", u"три дня"),
             ("7", u"неделю"), ("14", u"две недели"), ("30", u"месяц"),
             ("90", u"три месяца"), ("180", u"полгода"))


class MyForm(forms.ModelForm):
    def as_div(self):
        "Returns this form rendered as HTML <div>s."
        return self._html_output(
            normal_row = u'<div%(html_class_attr)s>%(label)s %(field)s %(help_text)s %(errors)s</div>',
            error_row = u'<div class="error">%s</div>',
            row_ender = '</div>',
            help_text_html = u'<div class="hefp-text">%s</div>',
            errors_on_separate_row = False)


class UserForm(MyForm):
    class Meta:
        model = User
        exclude = ['date_joined',
                   'get_all_permissions',
                   'get_full_name',
                   'get_group_permissions',
                   'get_next_by_date_joined',
                   'get_next_by_last_login',
                   'get_previous_by_date_joined',
                   'get_previous_by_last_login',
                   'get_profile',
                   'get_short_name',
                   'get_username',
                   'groups',
                   'has_module_perms',
                   'has_perm',
                   'has_perms',
                   'has_usable_password',
                   'id',
                   'is_active',
                   'is_anonymous',
                   'is_authenticated',
                   'is_staff',
                   'is_superuser',
                   'last_login',
                   'logentry_set',
                   'natural_key',
                   'objects',
                   'password',
                   'user_permissions',
                   'validate_unique']

def validate_spam(text):
    spam_words = SpamWord.objects.all()
    for sw in spam_words:
        if sw.word in text:
            raise ValidationError((u'Обнаружен спам'), code='invalid')


class FastUserForm(MyForm):
    mail = forms.CharField(label=u'mail', required=False)
    
    class Meta:
        model = UserData
        fields = ['email', 'first_name']


class AdvertForm(MyForm):
    category = forms.ModelChoiceField(label=u'Категория',
            queryset=Category.objects.filter(parent__isnull=False))
    main_text = forms.CharField(validators=[validate_spam],
                                widget=forms.Textarea, label =u'Текст объявления')
    title = forms.CharField(validators=[validate_spam], label=u'Заголовок')

    class Meta:
        model = Advert
        fields = [
            'title',
            'category',
            'price_uah',
            'price_usd',
            'price_unit',
            'main_text',
            'contact_name',
            'raw_phones',
            'seller',
            'city',
            'metro',
            'sublocality',
            'street',
            'latitude',
            'longitude',
        ]
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }


class ExtraFlatForm(MyForm):
    class Meta:
        model = ExtraFlat
        exclude = ['advert']


class PhoneForm(MyForm):
    class Meta:
        model = Phone
        exclude = ['owner', 'agent']


class ExtraHouseForm(MyForm):
    class Meta:
        model = ExtraHouse
        exclude = ['advert']


class ExtraLotForm(MyForm):
    class Meta:
        model = ExtraLot
        exclude = ['advert']


class ExtraRentForm(MyForm):
    class Meta:
        model = ExtraRent
        exclude = ['advert']


class ExtraCommercialForm(MyForm):
    class Meta:
        model = ExtraCommercial
        exclude = ['advert']

class NoneForm(forms.Form):

    def save(self):
      pass


FORM_BY_CAT = {0:[NoneForm,],
               11:[ExtraFlatForm, ],  # sale
               12:[ExtraFlatForm, ],
               13:[ExtraFlatForm, ],
               14:[ExtraHouseForm, ],
               15:[NoneForm],
               16:[ExtraLotForm, ],
               17:[ExtraCommercialForm, ],
               21:[ExtraFlatForm, ExtraRentForm],  # rent
               22:[ExtraFlatForm, ExtraRentForm],
               23:[ExtraFlatForm, ExtraRentForm],
               24:[ExtraHouseForm, ExtraRentForm],
               25:[NoneForm],
               26:[ExtraLotForm, ExtraRentForm],
               27:[ExtraRentForm,ExtraCommercialForm],
               31:[ExtraFlatForm],  #buy
               32:[ExtraFlatForm],
               33:[ExtraFlatForm],
               34:[ExtraHouseForm],
               36:[ExtraLotForm],
               37:[ExtraCommercialForm],
               41:[ExtraFlatForm],  #get by
               42:[ExtraFlatForm],
               43:[ExtraFlatForm],
               44:[ExtraHouseForm],
               46:[ExtraLotForm],
               47:[ExtraCommercialForm]
}

def get_extra_model(category_id=None, data=None, advert=None):
    """magic of OOP"""
    if int(category_id) is 0:
        if advert:
            category_id = advert.category.pk
    forms = []
    for form in FORM_BY_CAT.get(int(category_id), [NoneForm, ]):
        if data and not advert:  # if isset post request
            forms.append(form(data=data))
        else:
            if advert:  # if we do redact the advert for additional model
                frm = form()
                exstra = frm._meta.model
                try:
                    exstra, c = exstra.objects.get_or_create(advert=advert)
                    forms.append(form(data=data, instance=exstra))
                except exstra.DoesNotExist:
                    print "FUCK!!!"
                    exstra = frm._meta.model
                    forms.append(form())
            else:
                forms.append(form())
    return forms

def extra_valid(forms):
    return len([x for x in forms if x.is_valid()])==len(forms)
    for form in forms:
        if not form.is_valid():
            return False
    return True

def extra_save(forms, advert):
    res = []
    for form in forms:
        # import pdb; pdb.set_trace()
        try:
            model = form.save(commit=False)
            model.advert = advert
            model.save()
            res.append(model)
        except Exception, ex:
            print "ERRROR!!!!!", ex
            # exstra = frm._meta.model
            # exstra = exstra.objects.get(advert=advert)
            # instance=advert
            # logger.error(ex)
    return  res
    #return  form.save() for form in forms 
    # tatata

class FilterForm(forms.Form):

    def __init__(self, *args, **kwargs):
        city_object = kwargs.pop('city_object', None)
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['term_search'].initial = '30'
        if city_object:
            all_locations = Sublocality.objects.filter(city__id=city_object.id)
            big_sublocality = BigSublocality.objects.filter(
                    city_id=city_object.id).order_by('id')
            all_metro = Metro.objects.filter(city__id=city_object.id)
            metro_lines = MetroLine.objects.filter(city__id=city_object.id)
            
            self.fields['province'] = ModelMultipleChoiceField(
                    label=u'Областной центр',
                    queryset=all_locations.filter(in_city=False),
                    widget=CheckboxSelectMultiple(attrs={'form': 'search_query'}))
            
            self.fields['bigsubloc'] = ModelMultipleChoiceField(
                widget=CheckboxSelectMultiple(attrs={'form': 'search_query'}),
                queryset=big_sublocality)

            for i, item in enumerate(big_sublocality):
                self.fields[str(i)+'subloc'] = ModelMultipleChoiceField(
                    widget=CheckboxSelectMultiple(attrs={'form': 'search_query'}),
                    queryset=all_locations.filter(big_sublocality=item.id))
                
            # self.fields['sublocality'] = ModelMultipleChoiceField(
            #     widget=CheckboxSelectMultiple(attrs={'form':'search_query'}),
            #     queryset=all_locations)
            for i, item in enumerate(metro_lines):
                self.fields[str(i)+'metro_line'] = ModelMultipleChoiceField(
                    widget=CheckboxSelectMultiple(attrs={'form': 'search_query'}),
                    queryset=all_metro.filter(line=item.id).order_by('sequence_number'))
    term_search = forms.ChoiceField(choices=TERM_LIST,
                                    widget=Select(attrs={'form': 'search_query'}))
    rooms_num = forms.MultipleChoiceField(required=False,
            widget=CheckboxSelectMultiple(attrs={'form': 'search_query'}),
            choices=CHECKBOX_CHOICES,
            label=u'Число комнат')
    min_price = forms.DecimalField(label=u'от', required=False,
            widget=forms.NumberInput(attrs={'step':'100', 'form': 'search_query'}))
    max_price = forms.DecimalField(label=u'до', required=False,
            widget=forms.NumberInput(attrs={'form': 'search_query'}))
    query = forms.CharField(widget=forms.TextInput(attrs={'form': 'search_query'}))
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES, 
            widget=forms.Select(attrs={'form': 'search_query',}))
    sort_obj = forms.ChoiceField(choices=SELECT_OBJ, 
            widget=forms.Select(attrs={'form': 'search_query',}))
    sort_level = forms.ChoiceField(choices=SELECT_LEVEL, 
            widget=forms.Select(attrs={'form': 'search_query',}))
    object_type = ModelMultipleChoiceField(queryset=ObjectType.objects.all(),
            widget=CheckboxSelectMultiple(attrs={'form': 'search_query'}))
    object_all = forms.ChoiceField(choices=OBJ_ALL, 
            widget=forms.Select(attrs={'form': 'search_query',}))
    action = forms.ChoiceField(choices=ACT, 
            widget=forms.Select(attrs={'form': 'search_query',}))
    woagent = forms.BooleanField(widget=forms.CheckboxInput(attrs={'form': 'search_query'}))
    prozvon = forms.BooleanField(widget=forms.CheckboxInput(attrs={'form': 'search_query'}))
    city = ModelChoiceField(queryset=City.objects.all(),
                            label=u'Город', 
                            required=True,
                            help_text=u'',
                            empty_label=None,
                            widget=forms.Select(attrs={'form': 'search_query'}))
    rent_term = forms.DecimalField(widget=Select(choices=TERM_CHOICES,
                                    attrs={'form': 'search_query'}))
    text_filter = forms.CharField(widget=forms.TextInput(attrs={'form': 'search_query',
                                    'placeholder': u'Поиск по слову'})) 
    hide_show_notes = forms.DecimalField(widget=Select(choices=SHOW_NOTE_CHOICES,
                                            attrs={'form': 'search_query'}),)
    pro_color = forms.MultipleChoiceField(choices=PRO_COLORS,
                                          widget=CheckboxSelectMultiple(
                                                attrs={'form': 'search_query'}))
    pro_comment = forms.BooleanField(widget=forms.CheckboxInput(
                                        attrs={'form': 'search_query'}))
    new_building = forms.BooleanField(widget=forms.CheckboxInput(attrs={'form': 'search_query'}))
    house_type = forms.MultipleChoiceField(required=False, choices=HOUSE_TYPE,
        widget=forms.CheckboxSelectMultiple(attrs={'form': 'search_query', 'class': 'hohouse'}))
