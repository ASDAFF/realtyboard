# -*- coding: utf-8 -*-
from django import template
from django.template.loader import get_template

register = template.Library()

@register.simple_tag
def pay_btns_tag(prices):
    t = get_template('personal/templatetags/pay_btns.html')
    return t.render(template.Context({'prices': prices}))