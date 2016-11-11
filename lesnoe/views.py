from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from lesnoe.models import Gallery, Project, PageText


class FirstPage(TemplateView):
    def get_context_data(self, *args, **kwargs):
        context = super(FirstPage, self).get_context_data(*args, **kwargs)
        context['text'] = PageText.objects.get(id=1)
        context['spoiler_text'] = PageText.objects.get(id=3)
        return context
        
        
class Infrastr(TemplateView):
    def get_context_data(self, *args, **kwargs):
        context = super(Infrastr, self).get_context_data(*args, **kwargs)
        context['text'] = PageText.objects.get(id=2)
        return context

class GalleryView(ListView):
    model = Gallery
    template_name = 'lesnoe/gallery.html'
    
    
class ProjectList(ListView):
    model = Project
    template_name='lesnoe/project_list.html'
    

class ProjectDetail(DetailView):
    model = Project
    template_name = 'lesnoe/project.html'
    