# -*- coding: utf-8 -*-
from board.models import City

big_sublocalities = (
    (u'Харьков', (
        u'Центральный р-н',
        u'Напр-е Белгородское',
        u'Направление Н.Бавария',
        u'Направление Хол.Гора',
        u'Направление Аэропорт',
        u'Направление Рогань',
        u'Направление Салтовка',
        u'Направление Алексеевка',
        u'Пригород')),
    (u'Киев', (
        u'Голосеевский р-н',
        u'Дарницкий р-н',
        u'Днепровский р-н',
        u'Деснянский р-н',
        u'Оболонский р-н',
        u'Печерский р-н',
        u'Подольский р-н',
        u'Святошинский р-н',
        u'Соломенский р-н',
        u'Шевченковский р-н',)),
)

def import_data():
    for city_name, big_subloc_list in big_sublocalities:
        cc = City.objects.get(name=city_name)
        for big_subloc_name in big_subloc_list:
            cc.bigsublocality_set.create(name=big_subloc_name)
        