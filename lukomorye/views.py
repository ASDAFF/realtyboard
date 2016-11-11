from django.views.generic import TemplateView
from lukomorye.models import GallaryModel, SiteText

class GallaryView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(GallaryView, self).get_context_data(**kwargs)
        context['gallary'] = GallaryModel.objects.all().order_by('place')
        return context
        
class HomeView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['text1'] = SiteText.objects.get(id=1)
        return context