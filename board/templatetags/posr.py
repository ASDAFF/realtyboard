# -*- coding: utf-8 -*-
from django import template
from django.template.loader import get_template
from django.template import Context


register = template.Library()

@register.simple_tag
def posr():

    status = 'посредник'
    phone = '0000'
    t = get_template('board/templatetags/posr.html')
    html = t.render(Context({'phone': phone, 'status': status}))
    return html
