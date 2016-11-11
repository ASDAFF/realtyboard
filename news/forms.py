# encoding: utf-8
from django import forms
from board.utils import parse_int
from ckeditor.widgets import CKEditorWidget
from news.models import News, Comment, BlackList

class NewsForm(forms.ModelForm):
    article = forms.CharField(widget=CKEditorWidget(config_name='article'))
    foreword = forms.CharField(widget=CKEditorWidget(config_name='foreword'))

    class Meta:
        model = News
        exclude = ('author',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ['pub_date', 'news']


class BlackPostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BlackPostForm, self).__init__(*args, **kwargs)
        self.fields['phone'] = forms.CharField(required=True, help_text='', 
            label = u'Телефоны мошенников',
            widget=forms.TextInput(
                attrs={'placeholder': u'несколько номеров указывайте через запятую'}),)
    
    def clean_phone(self):
        str_phones = self.cleaned_data['phone'].split(',')
        phones = []
        for str_phone in str_phones:
            phone = parse_int(str_phone)
            if len(str(phone)) == 9:
                phones.append(phone)
        if len(phones) == 0: 
            raise forms.ValidationError(u'Короткий номер, возможно нужно дописать код корода')       
    
    class Meta:
        model = BlackList
        fields = ['city', 'address', 'phone', 'text']
