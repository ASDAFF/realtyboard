from django.shortcuts import render_to_response
from importdb.utils import *
#import datetime

def index(request):
    data = import_db()
    return render_to_response('importdb/index.html',{'data': data})