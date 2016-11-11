from django.shortcuts import render, render_to_response
from django.template import RequestContext
import datetime

def example(request):
    adverts_list = 'ext'
    generation_date = datetime.datetime.now().isoformat()
    return render_to_response('tour/example.html',
                              {'adverts_list': adverts_list,
                               'generation_date':generation_date},
                               context_instance=RequestContext(request))
