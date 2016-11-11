# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines for those models you wish to give write DB access
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class Adminsettings(models.Model):
    id = models.IntegerField(primary_key=True)
    nav_kol_users = models.IntegerField()
    nav_kol_stats = models.IntegerField()
    nav_kol_sait = models.IntegerField()
    nav_kol_baza = models.IntegerField()
    nav_kol_baza_site = models.IntegerField()
    nav_kol_baza_site_prosmotr = models.IntegerField()
    nav_kol_adwerts = models.IntegerField()
    nav_kol_users_sait = models.IntegerField()
    title = models.CharField(max_length=500)
    class Meta:
        managed = False
        db_table = 'adminsettings'

class Adwerts(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    expiration = models.DateField()
    adw_id = models.IntegerField()
    target = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'adwerts'

class Balkons(models.Model):
    id = models.IntegerField(primary_key=True)
    balkon = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'balkons'

class Bases(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    expiration = models.DateField()
    class Meta:
        managed = False
        db_table = 'bases'

class Bazecatids(models.Model):
    #id = models.IntegerField()
    name = models.CharField(max_length=20)
    class Meta:
        managed = False
        db_table = 'bazecatids'

class Bazeprosmotrs(models.Model):
    id = models.IntegerField(primary_key=True)
    rajon = models.CharField(max_length=30)
    objek = models.CharField(max_length=20)
    text = models.CharField(max_length=5000)
    telefon = models.CharField(max_length=50)
    vipusk = models.CharField(max_length=10)
    rubrik = models.CharField(max_length=20)
    chast = models.IntegerField()
    prozvon = models.IntegerField()
    data_prozvona = models.CharField(max_length=10)
    class Meta:
        managed = False
        db_table = 'bazeprosmotrs'

class Bazes(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=10)
    chast = models.IntegerField()
    catid = models.CharField(max_length=10)
    year = models.CharField(max_length=4)
    file_name = models.CharField(max_length=30)
    class Meta:
        managed = False
        db_table = 'bazes'

class Catdescriptions(models.Model):
    id = models.IntegerField(primary_key=True)
    cat_description = models.TextField()
    cat_title = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'catdescriptions'

class Cats(models.Model):
    id = models.IntegerField(primary_key=True)
    cat = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'cats'

class Cherniyspisoks(models.Model):
    id = models.IntegerField(primary_key=True)
    adress = models.CharField(max_length=500)
    telefon = models.CharField(max_length=500)
    text = models.CharField(max_length=5000)
    date = models.DateTimeField()
    user_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'cherniyspisoks'

class Cities(models.Model):
    id = models.IntegerField(primary_key=True)
    city = models.CharField(max_length=50)
    cityeng = models.CharField(max_length=20)
    cityvpadege = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'cities'

class ComTel(models.Model):
    id = models.IntegerField(primary_key=True)
    phone = models.CharField(max_length=16)
    class Meta:
        managed = False
        db_table = 'com_tel'

class Copywritings(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    mestopol = models.CharField(max_length=4)
    data = models.CharField(max_length=10)
    simvols = models.CharField(max_length=7)
    sale = models.IntegerField()
    oplata = models.IntegerField()
    url = models.CharField(max_length=50)
    ancors1 = models.CharField(max_length=20)
    ancors2 = models.CharField(max_length=20)
    ancors3 = models.CharField(max_length=20)
    ancors4 = models.CharField(max_length=20)
    ancors5 = models.CharField(max_length=20)
    ancors6 = models.CharField(max_length=20)
    ancors7 = models.CharField(max_length=20)
    ancors8 = models.CharField(max_length=20)
    ancors9 = models.CharField(max_length=20)
    ancors10 = models.CharField(max_length=20)
    class Meta:
        managed = False
        db_table = 'copywritings'

class Countries(models.Model):
    id = models.IntegerField(primary_key=True)
    country = models.CharField(max_length=20)
    class Meta:
        managed = False
        db_table = 'countries'

class Hozes(models.Model):
    id = models.IntegerField(primary_key=True)
    tel = models.IntegerField(unique=True)
    who = models.TextField()
    opisanie = models.CharField(max_length=255)
    date = models.DateField()
    class Meta:
        managed = False
        db_table = 'hozes'

class Kharkovcats(models.Model):
    kharkov_id = models.IntegerField()
    ncat_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'kharkovcats'

class Kharkovclients(models.Model):
    id = models.IntegerField(primary_key=True)
    region_id = models.IntegerField()
    city_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'kharkovclients'

class Kharkovdirections(models.Model):
#    id = models.IntegerField(unique=True)
    direction = models.CharField(max_length=40)
    class Meta:
        managed = False
        db_table = 'kharkovdirections'

class Kharkovimages(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    city_id = models.IntegerField()
    main = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'kharkovimages'

class Kharkovlinemetros(models.Model):
    id = models.IntegerField(primary_key=True)
    linemetro = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'kharkovlinemetros'

class Kharkovmetrostations(models.Model):
    id = models.IntegerField(primary_key=True)
    metrostation = models.CharField(max_length=40)
    class Meta:
        managed = False
        db_table = 'kharkovmetrostations'

class Kharkovoutregions(models.Model):
    id = models.IntegerField(primary_key=True)
    outregion = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'kharkovoutregions'

class Kharkovrayons(models.Model):
#    id = models.IntegerField(unique=True)
    direction_id = models.IntegerField()
    rayon = models.CharField(max_length=40)
    class Meta:
        managed = False
        db_table = 'kharkovrayons'

class Kharkovregionbazas(models.Model):
#    id = models.IntegerField()
    orientir = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'kharkovregionbazas'

class Kharkovregions(models.Model):
#    id = models.IntegerField(unique=True)
    region = models.CharField(max_length=50)
    direction_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'kharkovregions'

class Kharkovs(models.Model):
    id = models.IntegerField(primary_key=True)
    city = models.IntegerField()#models.IntegerField()
    cityeng = models.CharField(max_length=50)
    cat_id = models.IntegerField() #models.IntegerField()
    title = models.CharField(max_length=255)
    typeobject = models.IntegerField()
    object = models.IntegerField()
    operation = models.IntegerField()
    description = models.TextField()
    targetplant = models.IntegerField()
    docplant = models.IntegerField()
    komnat = models.IntegerField()
    type = models.IntegerField()
    uchstok = models.IntegerField()
    flor = models.IntegerField()
    allfloor = models.IntegerField()
    state = models.IntegerField()
    furniture = models.IntegerField()
    internet = models.CharField(max_length=4)
    heating = models.IntegerField()
    water = models.IntegerField()
    gens = models.IntegerField()
    wood = models.IntegerField()
    woodto = models.IntegerField()
    pond = models.IntegerField()
    pondto = models.IntegerField()
    electro = models.IntegerField()
    sewage = models.IntegerField()
    lift = models.IntegerField()
    plan = models.IntegerField()
    balkon = models.IntegerField()
    wall = models.IntegerField()
    overlap = models.IntegerField()
    period_rent = models.IntegerField()
    cost = models.CharField(max_length=30)
    currency = models.IntegerField()
    costyp = models.IntegerField()
    per_rent = models.IntegerField()
    streets_id = models.IntegerField()
    outstreet_id = models.CharField(max_length=100)
    region_id = models.IntegerField()
    home = models.CharField(max_length=10)
    metro = models.IntegerField()
    timemetro = models.IntegerField()
    linemetro = models.IntegerField()
    howlong = models.IntegerField()
    phone1 = models.CharField(max_length=50)
    phone2 = models.CharField(max_length=50)
    skype = models.CharField(max_length=50)
    mail = models.CharField(max_length=50)
    isq = models.CharField(max_length=50)
    contact = models.CharField(max_length=50)
    additionally = models.TextField()
    s = models.IntegerField()
    slive = models.IntegerField()
    skitchen = models.IntegerField()
    hometel = models.CharField(max_length=4)
    washing = models.CharField(max_length=4)
    conditioner = models.CharField(max_length=4)
    tv = models.CharField(max_length=4)
    frig = models.CharField(max_length=4)
    garage = models.CharField(max_length=4)
    cellar = models.CharField(max_length=4)
    shome = models.CharField(max_length=50)
    splant = models.CharField(max_length=50)
    data = models.DateTimeField()
    status = models.IntegerField()
    user_id = models.IntegerField()
    image_id = models.CharField(max_length=255)
    count_image = models.IntegerField()
    up = models.DateTimeField()
    zametka_id = models.IntegerField()
    
#    manger = self.objects.using('old')
    
    class Meta:
        managed = False
        db_table = 'kharkovs'

class Kharkovstreets(models.Model):
    id = models.IntegerField(primary_key=True)
    street = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'kharkovstreets'

class Kievclients(models.Model):
    id = models.IntegerField(primary_key=True)
    region_id = models.IntegerField()
    city_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'kievclients'

class Kievimages(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    city_id = models.IntegerField()
    main = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'kievimages'

class Kievmetrostations(models.Model):
    id = models.IntegerField(primary_key=True)
    metrostation = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'kievmetrostations'

class Kievregions(models.Model):
    id = models.IntegerField(primary_key=True)
    region = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'kievregions'

class Kievs(models.Model):
    id = models.IntegerField(primary_key=True)
    city = models.IntegerField()
    cityeng = models.CharField(max_length=50)
    cat_id = models.IntegerField()
    title = models.CharField(max_length=255)
    typeobject = models.IntegerField()
    object = models.IntegerField()
    operation = models.IntegerField()
    description = models.TextField()
    targetplant = models.IntegerField()
    docplant = models.IntegerField()
    komnat = models.IntegerField()
    type = models.IntegerField()
    uchstok = models.IntegerField()
    flor = models.IntegerField()
    allfloor = models.IntegerField()
    state = models.IntegerField()
    furniture = models.IntegerField()
    internet = models.CharField(max_length=4)
    heating = models.IntegerField()
    water = models.IntegerField()
    gens = models.IntegerField()
    wood = models.IntegerField()
    woodto = models.IntegerField()
    pond = models.IntegerField()
    pondto = models.IntegerField()
    electro = models.IntegerField()
    sewage = models.IntegerField()
    lift = models.IntegerField()
    plan = models.IntegerField()
    balkon = models.IntegerField()
    wall = models.IntegerField()
    overlap = models.IntegerField()
    period_rent = models.IntegerField()
    cost = models.CharField(max_length=30)
    currency = models.IntegerField()
    costyp = models.IntegerField()
    per_rent = models.IntegerField()
    streets_id = models.CharField(max_length=255)
    region_id = models.IntegerField()
    home = models.CharField(max_length=10)
    metro = models.IntegerField()
    timemetro = models.IntegerField()
    linemetro = models.IntegerField()
    howlong = models.IntegerField()
    phone1 = models.CharField(max_length=50)
    phone2 = models.CharField(max_length=50)
    skype = models.CharField(max_length=50)
    mail = models.CharField(max_length=50)
    isq = models.CharField(max_length=50)
    contact = models.CharField(max_length=50)
    additionally = models.TextField()
    s = models.IntegerField()
    slive = models.IntegerField()
    skitchen = models.IntegerField()
    hometel = models.CharField(max_length=4)
    washing = models.CharField(max_length=4)
    conditioner = models.CharField(max_length=4)
    tv = models.CharField(max_length=4)
    frig = models.CharField(max_length=4)
    garage = models.CharField(max_length=4)
    cellar = models.CharField(max_length=4)
    shome = models.CharField(max_length=50)
    splant = models.CharField(max_length=50)
    data = models.DateTimeField()
    status = models.IntegerField()
    user_id = models.IntegerField()
    image_id = models.CharField(max_length=255)
    up = models.DateTimeField()
    zametka_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'kievs'

class Lifts(models.Model):
    id = models.IntegerField(primary_key=True)
    lift = models.CharField(max_length=20)
    class Meta:
        managed = False
        db_table = 'lifts'

class Logs(models.Model):
    id = models.IntegerField(primary_key=True)
    order_id = models.CharField(max_length=255)
    user_id = models.IntegerField()
    merchant_id = models.CharField(max_length=255)
    transaction_id = models.CharField(max_length=255)
    response_description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    days = models.IntegerField()
    type = models.CharField(max_length=255)
    target = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    currency = models.CharField(max_length=255)
    card = models.IntegerField()
    phone = models.IntegerField()
    adw_id = models.IntegerField()
    result = models.TextField()
    date = models.DateField()
    class Meta:
        managed = False
        db_table = 'logs'

class Messages(models.Model):
    id = models.IntegerField(primary_key=True)
    mes = models.TextField()
    class Meta:
        managed = False
        db_table = 'messages'

class Navigations(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    edit = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'navigations'

class Ncats(models.Model):
    id = models.IntegerField(primary_key=True)
    cat = models.CharField(max_length=150)
    class Meta:
        managed = False
        db_table = 'ncats'

class Numberofrooms(models.Model):
#    id = models.IntegerField()
    opisanie = models.CharField(max_length=15)
    class Meta:
        managed = False
        db_table = 'numberofrooms'

class Objects(models.Model):
    id = models.IntegerField(primary_key=True)
    object = models.CharField(max_length=25)
    class Meta:
        managed = False
        db_table = 'objects'

class Operations(models.Model):
    id = models.IntegerField(primary_key=True)
    operation = models.CharField(max_length=11)
    class Meta:
        managed = False
        db_table = 'operations'

class Otherimages(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    city_id = models.IntegerField()
    main = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'otherimages'

class Others(models.Model):
    id = models.IntegerField(primary_key=True)
    city = models.IntegerField()
    cityeng = models.CharField(max_length=50)
    cat_id = models.IntegerField()
    title = models.CharField(max_length=255)
    typeobject = models.IntegerField()
    object = models.IntegerField()
    operation = models.IntegerField()
    description = models.TextField()
    targetplant = models.IntegerField()
    docplant = models.IntegerField()
    komnat = models.IntegerField()
    type = models.IntegerField()
    uchstok = models.IntegerField()
    flor = models.IntegerField()
    allfloor = models.IntegerField()
    state = models.IntegerField()
    furniture = models.IntegerField()
    internet = models.CharField(max_length=4)
    heating = models.IntegerField()
    water = models.IntegerField()
    gens = models.IntegerField()
    wood = models.IntegerField()
    woodto = models.IntegerField()
    pond = models.IntegerField()
    pondto = models.IntegerField()
    electro = models.IntegerField()
    sewage = models.IntegerField()
    lift = models.IntegerField()
    plan = models.IntegerField()
    balkon = models.IntegerField()
    wall = models.IntegerField()
    overlap = models.IntegerField()
    period_rent = models.IntegerField()
    cost = models.CharField(max_length=30)
    currency = models.IntegerField()
    costyp = models.IntegerField()
    per_rent = models.IntegerField()
    streets_id = models.CharField(max_length=255)
    region_id = models.CharField(max_length=100)
    home = models.CharField(max_length=10)
    metro = models.IntegerField()
    timemetro = models.IntegerField()
    linemetro = models.IntegerField()
    howlong = models.IntegerField()
    phone1 = models.CharField(max_length=50)
    phone2 = models.CharField(max_length=50)
    skype = models.CharField(max_length=50)
    mail = models.CharField(max_length=50)
    isq = models.CharField(max_length=50)
    contact = models.CharField(max_length=50)
    additionally = models.TextField()
    s = models.IntegerField()
    slive = models.IntegerField()
    skitchen = models.IntegerField()
    hometel = models.CharField(max_length=4)
    washing = models.CharField(max_length=4)
    conditioner = models.CharField(max_length=4)
    tv = models.CharField(max_length=4)
    frig = models.CharField(max_length=4)
    garage = models.CharField(max_length=4)
    cellar = models.CharField(max_length=4)
    shome = models.CharField(max_length=50)
    splant = models.CharField(max_length=50)
    data = models.DateTimeField()
    status = models.IntegerField()
    user_id = models.IntegerField()
    image_id = models.CharField(max_length=255)
    up = models.DateTimeField()
    zametka_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'others'

class Overlaps(models.Model):
    id = models.IntegerField(primary_key=True)
    overlap = models.CharField(max_length=20)
    class Meta:
        managed = False
        db_table = 'overlaps'

class Owners(models.Model):
    id = models.IntegerField(primary_key=True)
    tel = models.IntegerField()
    opisanie = models.TextField()
    class Meta:
        managed = False
        db_table = 'owners'

class Plans(models.Model):
    id = models.IntegerField(primary_key=True)
    plan = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'plans'

class Poisks(models.Model):
    operation = models.IntegerField()
    object = models.IntegerField()
    kimnat = models.IntegerField()
    mistobl = models.IntegerField()
    id = models.IntegerField(primary_key=True)
    class Meta:
        managed = False
        db_table = 'poisks'

class Posredniks(models.Model):
    id = models.IntegerField(primary_key=True)
    tel = models.BigIntegerField(unique=True)
    opisanie = models.TextField()
    who = models.TextField()
    date = models.DateField()

    class Meta:
        managed = False
        db_table = 'posredniks'

class Prorings(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
    room = models.TextField()
    region = models.TextField()
    cost = models.TextField()
    phone1 = models.TextField()
    phone2 = models.TextField()
    phone3 = models.TextField()
    src = models.TextField()
    status = models.IntegerField()
    link = models.TextField()
    date = models.DateField()
    cat = models.IntegerField()
    site = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'prorings'

class Qualitys(models.Model):
    id = models.IntegerField(primary_key=True)
    quality = models.CharField(max_length=20)
    class Meta:
        managed = False
        db_table = 'qualitys'

class Rentedsolds(models.Model):
    id = models.IntegerField(primary_key=True)
    tel = models.CharField(max_length=50)
    opisanie = models.CharField(max_length=50)
    rubrika = models.CharField(max_length=50)
    zapis_id = models.IntegerField()
    dat_created = models.CharField(max_length=11)
    class Meta:
        managed = False
        db_table = 'rentedsolds'

class Roles(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=32)
    description = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'roles'

class RolesUsers(models.Model):
    user_id = models.AutoField(primary_key=True)
    role_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'roles_users'

class Rownos(models.Model):
#    id = models.IntegerField()
    id = models.IntegerField(primary_key=True)

    cat_id = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    komnat = models.IntegerField()
    type = models.IntegerField()
    flor = models.IntegerField()
    allfloor = models.IntegerField()
    quality = models.IntegerField()
    furniture = models.IntegerField()
    internet = models.IntegerField()
    heating = models.IntegerField()
    gens = models.IntegerField()
    electro = models.IntegerField()
    sewage = models.IntegerField()
    lift = models.IntegerField()
    period_rent = models.IntegerField()
    cost = models.CharField(max_length=30)
    currency = models.IntegerField()
    typecost = models.IntegerField()
    region = models.IntegerField()
    streets_id = models.CharField(max_length=255)
    region_id = models.IntegerField()
    outregion_id = models.IntegerField()
    home = models.CharField(max_length=10)
    metro = models.IntegerField()
    linemetro = models.IntegerField()
    howlongm = models.IntegerField()
    phone = models.IntegerField()
    phone1 = models.IntegerField()
    phone2 = models.IntegerField()
    email = models.TextField(db_column='Email') # Field name made lowercase.
    otherkontact = models.TextField()
    additionally = models.CharField(max_length=500)
    s = models.IntegerField()
    slive = models.IntegerField()
    skitchen = models.IntegerField()
    data = models.DateTimeField()
    status = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'rownos'

class Seoarticles(models.Model):
    id = models.IntegerField(primary_key=True)
    url = models.CharField(unique=True, max_length=255)
    text = models.TextField()
    class Meta:
        managed = False
        db_table = 'seoarticles'

class Sessions(models.Model):
    session_id = models.CharField(primary_key=True, max_length=127)
    last_activity = models.IntegerField()
    data = models.TextField()
    class Meta:
        managed = False
        db_table = 'sessions'

class Slandos(models.Model):
    # id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
    room = models.TextField()
    region = models.TextField()
    cost = models.TextField()
    phone1 = models.TextField()
    phone2 = models.TextField()
    phone3 = models.TextField()
    src = models.TextField()
    status = models.IntegerField()
    link = models.TextField()
    date = models.DateField()
    cat = models.IntegerField()
    ci_cat = models.IntegerField()
    site = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'slandos'

class Spam(models.Model):
    id = models.IntegerField(primary_key=True)
    spam = models.CharField(unique=True, max_length=255)
    class Meta:
        managed = False
        db_table = 'spam'

class States(models.Model):
    id = models.IntegerField(primary_key=True)
    state = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'states'

class Statistics(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateField()
    site = models.CharField(max_length=255)
    chast = models.IntegerField()
    rent = models.CharField(max_length=255)
    sale = models.CharField(max_length=255)
    sale_house = models.CharField(max_length=255)
    rent_comest = models.CharField(max_length=255)
    sale_comest = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'statistics'

class Stats(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    dat_created = models.DateTimeField()
    min = models.TextField()
    full = models.TextField()
    catid = models.IntegerField()
    opisanie = models.CharField(max_length=500)
    klucheviki = models.CharField(max_length=100)
    url = models.CharField(max_length=50)
    user_id = models.IntegerField()
    akt = models.IntegerField()
    banners = models.IntegerField()
    link = models.CharField(max_length=20)
    link_name = models.CharField(max_length=30)
    class Meta:
        managed = False
        db_table = 'stats'

class StatsCatid(models.Model):
    catid_id = models.IntegerField()
    catid = models.CharField(max_length=500)
    catid_url = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'stats_catid'

class Typeobjects(models.Model):
    id = models.IntegerField(primary_key=True)
    typeobject = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'typeobjects'

class Ulogins(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    network = models.CharField(max_length=255)
    identity = models.CharField(unique=True, max_length=255)
    class Meta:
        managed = False
        db_table = 'ulogins'

class UserRoles(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=13, blank=True)
    admin = models.IntegerField(blank=True, null=True)
    fullaccess = models.IntegerField(blank=True, null=True)
    spr = models.IntegerField(blank=True, null=True)
    stat = models.IntegerField(blank=True, null=True)
    board_moderator = models.IntegerField(blank=True, null=True)
    quest_moderator = models.IntegerField(blank=True, null=True)
    materials = models.IntegerField(blank=True, null=True)
    comments = models.IntegerField(blank=True, null=True)
    news = models.IntegerField(blank=True, null=True)
    forums_moderator = models.IntegerField(blank=True, null=True)
    comments_moderator = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'user_roles'

class UserTokens(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    user_agent = models.CharField(max_length=40)
    token = models.CharField(unique=True, max_length=40)
    type = models.CharField(max_length=100)
    created = models.IntegerField()
    expires = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'user_tokens'

class Users(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=50)
    email = models.CharField(unique=True, max_length=254)
    username = models.CharField(unique=True, max_length=32)
    password = models.CharField(max_length=64)
    remember = models.CharField(max_length=255)
    for_django_import = models.CharField(max_length=255)
    phone = models.CharField(max_length=100)
    from_whom = models.CharField(max_length=255)
    inow = models.CharField(max_length=100)
    dostup_k_baze = models.CharField(max_length=10)
    oplata = models.CharField(max_length=10)
    ip = models.CharField(max_length=15)
    ftp = models.IntegerField()
    ftp_pass = models.CharField(max_length=50)
    memoirs = models.TextField()
    total = models.DecimalField(max_digits=10, decimal_places=0)
    logins = models.IntegerField()
    last_login = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'users'
    
    def __unicode__(self):
        return "%s - %s" % (self.id, self.username)

class Walls(models.Model):
    id = models.IntegerField(primary_key=True)
    wall = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'walls'

class Years(models.Model):
    id = models.IntegerField(primary_key=True)
    year = models.CharField(max_length=30)
    class Meta:
        managed = False
        db_table = 'years'

