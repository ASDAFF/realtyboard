# -*- coding: utf-8 -*-
import re
from django import template
from board.models import Category, CHANGE_CITIES_NAME
from django.template.loader import get_template
from django.template import Context
from django.utils.encoding import force_unicode


from board.models import ProComment

register = template.Library()


@register.simple_tag
def category(city):
    cats = Category.objects.all().order_by('id').select_related('parent')
    t = get_template('board/templatetags/category.html')
    parentcats = []
    for cat in cats:
        if not cat.parent:
            cat.childcats = [x for x in cats if x.parent == cat]
            parentcats.append(cat)
    return t.render(Context({'cats': parentcats, 'city': city}))


@register.filter('intspace')
def intspace(value):
    """
    Преобразовывает целое число в строку, содержащую пробелы каждые три цифры.
    Например, становится '3 3000 000 'и '45 становится 45000 000'.
    Смотреть django.contrib.humanize
    """
    orig = force_unicode(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1> \g<2>', orig)
    if orig == new:
        return new
    else:
        return intspace(new)

@register.simple_tag
def city_seo(title, city_obj):
    if u' Харькове ' or u' Харьков ' in title:
        if city_obj['name'] in CHANGE_CITIES_NAME:
            city_name_ch = CHANGE_CITIES_NAME[city_obj['name']]
        else:
            city_name_ch = city_obj['name']+u'е'

        title = title.replace(u' Харьков ',' '+city_obj['name']+' ')
        title = title.replace(u' Харьков.',' '+city_obj['name']+'. ')
        title = title.replace(u'Харькове',city_name_ch)
    return title
        
@register.filter('phoneformat')
def phoneformat(value):
    v_str = str(value)
    v_len = len(v_str)
    if v_len == 9:
        return ''.join(('0', v_str[:2], ' ', v_str[2:5], ' ', v_str[5:7], ' ', v_str[7:]))
    elif v_len == 7:
        return ''.join((v_str[:3], ' ', v_str[3:5], ' ', v_str[5:]))
    elif v_len == 5 or v_len == 6:
        return ''.join((v_str[:2], ' ', v_str[2:4], ' ', v_str[4:]))
        

@register.filter('hide_mail')
def hide_mail(string):
    return re.sub(r'@.+', '', string)


@register.simple_tag
def sublocality_tag(filterform, big_subloc_list, city_obj):
    try:
        t = get_template('board/templatetags/'+city_obj['slug']+'_sublocality.html')
    except:
        t = get_template('board/templatetags/all_cities_sublocality.html')
    return t.render(Context({'filterform': filterform, 'big_subloc_list': big_subloc_list}))


@register.simple_tag
def metro_tag(filterform, metro_lines):
    t = get_template('board/templatetags/metro.html')
    return t.render(Context({'filterform': filterform, 'metro_lines': metro_lines}))
    
    
@register.simple_tag
def banner_tag(banner, a_class):
    t = get_template('board/templatetags/banner.html')
    return t.render(Context({'banner': banner, 'class': a_class}))
    
    
@register.simple_tag
def adv_comment(adv, phones, user):
    phone_comments = []
    for phone in phones:
        phone_comments += list(phone.procomment_set.filter(user=user))
    adv_comment = adv.procomment_set.filter(user=user).first()
    if phone_comments or adv_comment:
        t = get_template('board/templatetags/adv_comment.html')
        return t.render(Context({'adv_comment': adv_comment, 
                                 'phone_comments': set(phone_comments)}))
    else:
        return ''

@register.simple_tag
def adv_cached_comment(adv_comments, phones, user_comments):
    adv_comments = set(user_comments).intersection(adv_comments)
    adv_comment = list(adv_comments)[0] if adv_comments else None
    phone_comments = set()
    for phone in phones:
        phone_comments.update(phone.procomment_set.all())
    phone_comments = set(user_comments).intersection(phone_comments)
    if phone_comments or adv_comment:
        t = get_template('board/templatetags/adv_comment.html')
        return t.render(Context({'adv_comment': adv_comment, 
                                 'phone_comments': phone_comments}))
    else:
        return ''

@register.simple_tag
def phone_pro_color(phone, user):
    try:
        phone_color = phone.procolormark_set.get(user=user)
        return ' marked-phone ' + phone_color.color
    except:
        return ''

@register.simple_tag
def phone_cached_pro_color(phone, user):
    color_marks = phone.procolormark_set.all()
    for mark in color_marks:
        if mark.user_id == user.id:
            return ' marked-phone ' + mark.color
    return ''

@register.simple_tag
def advert_pro_color(advert, user):
    try:
        advert_color = advert.procolormark_set.get(user=user)
        return ' marked-obj ' + advert_color.color
    except:
        return ''

@register.simple_tag
def advert_cached_pro_color(advert, user):
    color_marks = advert.procolormark_set.all()
    for mark in color_marks:
        if mark.user_id == user.id:
            return ' marked-obj ' + mark.color
    return ''