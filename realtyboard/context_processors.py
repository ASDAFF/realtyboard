# -*- coding: utf-8 -*-
from board.models import City, MessageForUsers

def city(request):
    city_id = request.COOKIES.get('city_id', '20')
    # костыль от ошибки если в куки city_id запишется пустая строка
    if city_id:
        city_id = int(city_id)
    else:
        city_id = 20
    cities_list = City.objects.all().order_by('name')
    city = cities_list.get(id=city_id)
    path = request.path.split('/')
    for item in cities_list:
        if item.slug == path[1]:
            city = cities_list.get(slug=path[1])
            break
    context = {'cities_list': cities_list,
               'city_obj': {'name': city.name, 'slug': city.slug, 'id': city.id},
               'housecut': (14, 24),
               'flatcut': (11, 12, 21, 22),
              }
    for mes in MessageForUsers.objects.all():
        context['mesforuser' + str(mes.location)] = mes.text

    return context
