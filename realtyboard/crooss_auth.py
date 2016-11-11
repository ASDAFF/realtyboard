from django.contrib.auth import login
#from django.contrib.auth.models import
from board.models import User
from django.contrib.auth import *


# class CroossAuth(object):
    # def process_response(self, request, response):
        # user_id = request.POST.get('ctj', None)
        # print user_id
        # if user_id:
        #     user = User.objects.get(id=user_id)
        #     user.backend = 'django.contrib.auth.backends.ModelBackend'
        #     login(request, user)
        # # else:
        # #     #logout(request)
        # #     pass
        # response.set_cookie('current_city', '15', expires='100000')
        # return response