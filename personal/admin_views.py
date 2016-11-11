# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic.detail import DetailView

from personal.models import UserIP, UserData

# @staff_member_required
def user_data_detail(request, pk):
    user_data = UserData.objects.get(pk=id)
    return render(request, 'admin/personal/userdata/admin_user_detail.html', {'user_data': user_data})   
    
# class UserDataDetail(DetailView):
#     model = UserData
#     template_name = 'admin/personal/userdata/admin_user_detail.html'
    
#     def get_context_data(self, **kwargs):
#         context = super(UserDataDetail, self).get_context_data(**kwargs)
#         context[] = UserData.objects.get(id=kwargs['pk'])
#         return context
     
    
    

