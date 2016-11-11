# -*- coding: utf-8 -*-
import re
from django import template
from board.models import Poll
from django.template.loader import get_template
from django.template import Context
from django.utils.encoding import force_unicode
from importdb.models import Messages

register = template.Library()


@register.simple_tag
def poll():

    latest_poll_list = Poll.objects.order_by('-pub_date')[:5]
    t = get_template('board/templatetags/poll.html')
    html = t.render(Context({'latest_poll_list': latest_poll_list}))

    return html