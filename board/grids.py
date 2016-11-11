# encoding: utf-8

from board.models import Advert
from jqgrid.jqgrid import JqGrid
from django.core.urlresolvers import reverse_lazy

class AdvertGrid(JqGrid):

    model = Advert #   could also be a queryset
    fields = ['id', 'title', 'sublocality__name', 'main_text', 'date_of_update', 'price_uah',] 
    url = reverse_lazy('grid_handler')
    caption = 'Список объявлений' # optional
    colmodel_overrides = {
        'id': { 'editable': False, 'width':30 },
        'title': {'width': 350},
        'sublocality__name': {'width': 350},        
        'date_of_update': {'width': 150},
        'main_text': {'width': 450}
    }