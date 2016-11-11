# -*- coding: utf-8 -*-
from board.models import City, Metro, MetroLine

metro_lines = (
    (u'Харьков', (
        (u'Алексеевская', (
            (1, u'Алексеевская', 29),
            (2, u'23 августа', 1),
            (3, u'Ботанический сад', 5),
            (4, u'Научная', 15),
            (5, u'Госпром', 7),
            (5, u'Архитектора Бекетова', 4),
            (6, u'Площадь Восстания', 16),
            (7, u'Метростроителей им. Ващенко', 13),
        )),
        (u'Салтовская', (
            (10, u'Героев труда', 6),
            (11, u'Студенческая', 23),
            (12, u'Академика Павлова', 3),
            (13, u'Академика Барабашова', 2),
            (14, u'Киевская ', 11),
            (15, u'Пушкинская', 19),
            (16, u'Университет', 25),
            (17, u'Исторический музей', 10),
        )),
        (u'Холодногорско-Заводская', (
            (20, u'Холодная гора', 26),
            (21, u'Южный вокзал', 28),
            (22, u'Центральный рынок', 27),
            (23, u'Советская', 20),
            (24, u'Проспект Гагарина', 17),
            (25, u'Спортивная', 22),
            (26, u'Завод им. Малышева', 8),
            (27, u'Московский проспект', 14),
            (28, u'Маршала Жукова', 12),
            (29, u'Советской армии', 21),
            (30, u'Им. А.С. Масельского', 9),
            (31, u'Тракторный завод', 24),
            (32, u'Пролетарская', 18),
        )),
    )),
    (u'Днепропетровск', (
        (u'Центрально-Заводская', (
            (40, u'Коммунаровская'),
            (41, u'Проспект Свободы'),
            (42, u'Заводская'),
            (43, u'Металлургов'),
            (44, u'Метростроителей'),
            (45, u'Вокзальная'),
        )),
    )),
    (u'Киев', (
        (u'Святошинско-Броварская', (
            (50, u'Академгородок'),
            (51, u'Житомирская'),
            (52, u'Святошин'),
            (53, u'Нивки'),
            (54, u'Берестейская'),
            (55, u'Шулявская'),
            (56, u'Политехнический институт'),
            (57, u'Вокзальная'),
            (58, u'Университет'),
            (59, u'Театральная'),
            (60, u'Крещатик'),
            (61, u'Арсенальная'),
            (62, u'Днепр'),
            (63, u'Гидропарк'),
            (64, u'Левобережная'),
            (65, u'Дарница'),
            (66, u'Черниговская'),
            (67, u'Лесная'),
        )),
        (u'Куренёвско-Красноармейская', (
            (70, u'Героев Днепра'),
            (71, u'Минская'),
            (72, u'Оболонь'),
            (73, u'Петровка'),
            (74, u'Тараса Шевченко'),
            (75, u'Контрактовая площадь'),
            (76, u'Почтовая площадь'),
            (77, u'Площадь Независимости'),
            (78, u'Площадь Льва Толстого'),
            (79, u'Олимпийская'),
            (80, u'Дворец Украина'),
            (81, u'Лыбедская'),
            (82, u'Демиевская'),
            (83, u'Голосеевская'),
            (84, u'Васильковская'),
            (85, u'Выставочный центр'),
            (86, u'Ипподром'),
            (87, u'Теремки'),
        )),
        (u'Сырецко-Печерская', (
            (90, u'Сырец'),
            (91, u'Дорогожичи'),
            (92, u'Лукьяновская'),
            (93, u'Золотые ворота'),
            (94, u'Дворец спорта'),
            (95, u'Кловская'),
            (96, u'Печерская'),
            (97, u'Дружбы народов'),
            (98, u'Выдубичи'),
            (99, u'Славутич'),
            (100, u'Осокорки'),
            (101, u'Позняки'),
            (102, u'Харьковская'),
            (103, u'Вырлица'),
            (104, u'Бориспольская'),
            (105, u'Красный хутор'),
        )),
    )),
)


def import_data():
    for city_name, metros in metro_lines:
        cc = City.objects.get(name=city_name)
        print cc.name
        for metro_line, stations_list in metros:
            ml = cc.metroline_set.get(name=metro_line)
            print ' ', ml.name
            for station in stations_list:
                if len(station) == 3:
                    ms, created = cc.metro_set.get_or_create(name=station[1], id=station[2])
                else:
                    ms, created = cc.metro_set.get_or_create(name=station[1])
                ms.sequence_number = station[0]
                ms.line_id = ml.id
                ms.save()
                print '  ', ms.name, ml.id

def line_test():
    for city_name, metros in metro_lines:
        cc = City.objects.get(name=city_name)
        for metro_line, stations_list in metros:
            ml = cc.metroline_set.get(name=metro_line)
            print ' ', ml.name
            
        