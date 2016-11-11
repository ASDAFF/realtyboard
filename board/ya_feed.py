# -*- coding: utf-8 -*-
import datetime, os, re
from django.db.models import Q
from django.utils import timezone
from lxml import etree

from realtyboard.settings import MEDIA_ROOT
from board.models import Advert, ExtraFlat, ExtraHouse, ExtraLot
from board.templatetags.category import phoneformat

def create_ya_feed():
    feed_dir = os.path.join(MEDIA_ROOT, 'ya_feed')
    if not os.path.exists(feed_dir):
        os.makedirs(feed_dir)
    try:
        f = open(feed_dir+'/realty_feed.xml', 'w')
        realty_feed = etree.Element('realty-feed', nsmap={
            None:'http://webmaster.yandex.ru/schemas/feed/realty/2010-06'})
        gen_date = etree.SubElement(realty_feed, 'generation-date')
        gen_date.text = datetime.datetime.strftime(
            datetime.datetime.now(), format='%Y-%m-%dT%H:%M:%S+02:00')
        
        # ads = Advert.objects.filter(
        #     category_id__in=[11,14,16,21,24,26], 
        #     is_active=True).select_related('extraflat', 'extrahouse', 'extrarent', 'extrasale')
        
        ads = Advert.objects.filter(
            Q(category_id__in=[11,21]) & Q(extraflat__rooms_number__isnull=False)
            | Q(category_id=16) & (Q(sublocality__in_city=True) | Q(big_sublocality__isnull=False))
            | Q(category_id__in=[14,24])
            ).filter(date_of_update__gt=timezone.now()-datetime.timedelta(hours=6)
            ).exclude(Q(price_uah__isnull=True) | Q(price_uah=0) | Q(author_id=8606)
            ).select_related('extraflat', 'extrahouse', 'extralot')
        print ads.count()
        ads = ads.prefetch_related('phone_set', 'photo_set')
        for ad in ads:
            try:
                # ad = Advert.objects.filter(category_id=21).last()
                # ad = Advert.objects.get(id=406)
                # для городской недвижимости обязательны улица или метро
                # для загородной обязательны название населенного пункта
                offer = etree.SubElement(realty_feed, 'offer', attrib={'internal-id': str(ad.id)})
                y_type = etree.SubElement(offer, 'type')
                y_type.text = ad.ya_type()
                property_type = etree.SubElement(offer, 'property-type')
                property_type.text = u'жилая'
                category = etree.SubElement(offer, 'category')
                category.text = ad.ya_category()
                url = etree.SubElement(offer, 'url')
                url.text = 'http://ci.ua' + ad.get_absolute_url()
                creation_date = etree.SubElement(offer, 'creation-date')
                creation_date.text = datetime.datetime.strftime(
                    ad.creation_date, format='%Y-%m-%dT%H:%M:%S+02:00')
                last_update_date = etree.SubElement(offer, 'last-update-date')
                last_update_date.text = datetime.datetime.strftime(
                    ad.date_of_update, format='%Y-%m-%dT%H:%M:%S+02:00')
                # expire_date = etree.SubElement(offer, 'expire_date') // необязательный параметр
                # expire_date.text = datetime.datetime.strftime(
                #     ad.date_of_update + datetime.timedelta(days=7),
                #     format='%Y-%m-%dT%H:%M:%S+02:00')
                
                location = etree.SubElement(offer, 'location')
                country = etree.SubElement(location, 'country')
                country.text = u'Украина'
                locality_name = etree.SubElement(location, 'locality-name')
                locality_name.text = ad.city.name
                
                if ad.sublocality_id:
                    non_admin_sub_locality = etree.SubElement(location, 'non-admin-sub-locality')
                    non_admin_sub_locality.text = ad.sublocality.name
                elif ad.big_sublocality_id:
                    non_admin_sub_locality = etree.SubElement(location, 'non-admin-sub-locality')
                    non_admin_sub_locality.text = ad.big_sublocality.name
                if ad.street:
                    address = etree.SubElement(location, 'address')
                    address.text = ad.street
                if ad.latitude and ad.longitude:
                    latitude = etree.SubElement(location, 'latitude')
                    latitude.text = str(ad.latitude)
                    longitude = etree.SubElement(location, 'longitude')
                    longitude.text = str(ad.longitude)
                if ad.metro:
                    metro = etree.SubElement(location, 'metro')
                    metro_name = etree.SubElement(metro, 'name')
                    metro_name.text = ad.metro.name
                    
                sales_agent = etree.SubElement(offer, 'sales-agent')
                if ad.contact_name:
                    sa_name = etree.SubElement(sales_agent, 'name')
                    sa_name.text = ad.contact_name
                for ph in ad.phone_set.all():
                    phone = etree.SubElement(sales_agent, 'phone')
                    phone.text = phoneformat(ph.phone)
                if ad.seller in [1,2,5]:
                    sa_category = etree.SubElement(sales_agent, 'category')
                    sa_category.text = u'агентство'
                elif ad.seller in [3,4]:
                    sa_category = etree.SubElement(sales_agent, 'category')
                    sa_category.text = u'владелец'
                
                price = etree.SubElement(offer, 'price')
                price_value = etree.SubElement(price, 'value')
                price_value.text = str(ad.price_uah).replace('-', '')
                currency = etree.SubElement(price, 'currency')
                currency.text = 'UAH'
                if ad.category in [21,24] and ad.extrarent:
                    if ad.extrarent.term == 1:
                        period = etree.SubElement(price, 'period')
                        period.text = u'день'
                    elif ad.extrarent.term == 2:
                        period = etree.SubElement(price, 'period')
                        period.text = u'месяц'
                
                square = None
                if ad.category.id in [11,21] and ad.extraflat:
                    if ad.extraflat.total_area:
                        area = etree.SubElement(offer, 'area')
                        area_value = etree.SubElement(area, 'value')
                        area_value.text = str(ad.extraflat.total_area).replace('-', '')
                        area_unit = etree.SubElement(area, 'unit')
                        area_unit.text = u'кв. м'
                    if  ad.extraflat.new_building:
                        new_flat = etree.SubElement(offer, 'new-flat')
                        new_flat.text = u'да'
                    if ad.extraflat.rooms_number:
                        rooms = etree.SubElement(offer, 'rooms')
                        rooms.text = str(ad.extraflat.rooms_number)
                        rooms_offered = etree.SubElement(offer, 'rooms-offered')
                        rooms_offered.text = str(ad.extraflat.rooms_number)
                    if ad.extraflat.floor:
                        floor = etree.SubElement(offer, 'floor')    
                        floor.text = str(ad.extraflat.floor).replace('-', '')
                    if ad.extraflat.floors:
                        floors_total = etree.SubElement(offer, 'floors-total')    
                        floors_total.text = str(ad.extraflat.floors).replace('-', '')
                elif ad.category.id in [14,24] and ad.extrahouse:
                    if ad.extrahouse.total_area:
                        area = etree.SubElement(offer, 'area')
                        area_value = etree.SubElement(area, 'value')
                        area_value.text = str(ad.extrahouse.total_area).replace('-', '')
                        area_unit = etree.SubElement(area, 'unit')
                        area_unit.text = u'сот'
                    if ad.extrahouse.lot_area:
                        lot_area = etree.SubElement(offer, 'lot-area')
                        lot_area_value = etree.SubElement(lot_area, 'value')
                        lot_area_value.text = str(ad.extrahouse.lot_area).replace('-', '')
                        lot_area_unit = etree.SubElement(lot_area, 'unit')
                        lot_area_unit.text = u'сот'
                    if ad.extrahouse.floors:
                        floors_total = etree.SubElement(offer, 'floors-total') 
                        floors_total.text = str(ad.extrahouse.floors).replace('-', '')
                    # if ad.extrahouse.water:
                    #     water_supply = etree.SubElement(offer, 'water-supply')
                    #     water_supply.text = u'да'
                    if ad.extrahouse.electricity in (u'в доме', u'на участке'):
                        electricity_supply = etree.SubElement(offer, 'electricity-supply')
                        electricity_supply.text = u'да'
                    if ad.extrahouse.gaz in (u'в доме', u'на участке'):
                        gas_supply = etree.SubElement(offer, 'gas-supply')
                        gas_supply.text = u'да'
                elif ad.category.id == 16 and ad.extralot:
                    if ad.extralot.lot_area:
                        lot_area = etree.SubElement(offer, 'lot-area')
                        lot_area_value = etree.SubElement(lot_area, 'value')
                        lot_area_value.text = str(ad.extralot.lot_area).replace('-', '')
                        lot_area_unit = etree.SubElement(lot_area, 'unit')
                        lot_area_unit.text = u'сот.'
                        if ad.extralot.electricity == u'на участке':
                            electricity_supply = etree.SubElement(offer, 'electricity-supply')
                            electricity_supply.text = u'да'
                        if ad.extralot.gaz == u'на участке':
                            gas_supply = etree.SubElement(offer, 'gas-supply')
                            gas_supply.text = u'да'
                if ad.photo_set.all():
                    for photo in ad.photo_set.all():
                        image = etree.SubElement(offer, 'image')
                        image.text = 'http://ci.ua/media/' + str(photo.photo)
                description = etree.SubElement(offer, 'description')
                description.text = re.sub(r'[^\w\s()\'\"/:;.,&><!-]', '', ad.main_text)
            except ExtraFlat.DoesNotExist:
                continue
            except ExtraHouse.DoesNotExist:
                pass    
            except ExtraLot.DoesNotExist:
                pass
        f.write(etree.tostring(realty_feed, pretty_print=True, 
            encoding='utf-8', xml_declaration=True))
    finally:
        f.close()