# -*- coding: utf-8 -*-
import base64, datetime, hashlib
import xml.etree.ElementTree as xee
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group
from django.core.context_processors import request
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, EmailMessage
from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
from liqpay.liqpay import LiqPay
from random import choice

USER_ACTION_CHOICES = ((1, u'вкл'), (2, u'выкл'),)


class ServicePrice(models.Model):
    kind = models.CharField(max_length=25)
    price = models.IntegerField()
    days = models.IntegerField()
    title = models.CharField(max_length=40, blank=True)
    for_btn = models.CharField(max_length=15, blank=True)
    
    
class PaidService(models.Model):
    name = models.CharField(max_length=30)
    ru_name = models.CharField(max_length=40)
    prices = models.ManyToManyField(ServicePrice)
    city = models.OneToOneField('board.City', blank=True, null=True)
    
    def __unicode__(self):
        return self.ru_name


class UserDataManager(BaseUserManager):
    def create_user(self, username, email, password, first_name, last_name=''):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            username=username,
            email=UserDataManager.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            remember=password,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, first_name, last_name, password):
        user = self.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.rememder = ''
        user.save(using=self._db)
        return user


class UserData(AbstractBaseUser):
    email = models.EmailField('email', max_length=75, unique=True)
    username = models.CharField(u'Логин', max_length=30, unique=True)
    first_name = models.CharField(u'Имя', max_length=30)
    last_name = models.CharField(u'Фамилия', max_length=30, blank=True)
    is_active = models.BooleanField(u'Активный', default=True)
    is_admin = models.BooleanField(default=False)
    creation_date = models.DateField(u'Дата регистрации', default=timezone.now)
    counting_logins = models.IntegerField(verbose_name=u'Число входов', default=0)
    source = models.CharField(verbose_name=u'Как узнал о ЦИ', max_length=20, blank=True)
    current_balance = models.DecimalField(verbose_name=u'Текущий баланс', default=0,
                                          max_digits=6, decimal_places=2)
    favorite_adv = models.ManyToManyField("board.Advert", verbose_name=u'Избранные объявления')
    groups = models.ManyToManyField(Group, verbose_name=u'Группы', blank=True)
    remember = models.CharField(u'Пароль', max_length=255, blank=True)
    memoirs = models.TextField('memoirs', max_length=100000, blank=True)
    services = models.ManyToManyField(PaidService, null=True, blank=True)
    token = models.CharField(max_length=100, null=True, blank=True)
    objects = UserDataManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    def get_full_name(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def get_short_name(self):
        return u'%s' % self.first_name

    def __unicode__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def is_abonent(self, service_id=None, city_id=None):
        try:
            if service_id:
                self.services.get(id=service_id)
            elif city_id:
                self.services.get(city_id=city_id)
            elif self.services.filter(name__startswith='base_'):
                return True
            else:
                return False
            return True
        except ObjectDoesNotExist:
            return False

    def is_superuser(self):
        # or self.groups.get(name='redaktor')
        if self.groups.get(name='admin'):
            return True
        else:
            return False

    def is_redactor_or_admin(self):
        # or self.groups.get(name='redaktor')
        if self.groups.get(name='admin'):
            return True
        else:
            return False

    def set_ab_status(self, service, term=0, info=''):
        """Установить статус абонента, принимает срок в днях и комментарий,
        сохраняет запись об операции в UserOperation"""
        expiration_date = self.get_exp_date(service.id)
        if self.is_abonent(service.id) and expiration_date:
            info = u'Доступ продлен ' + info
            exp_date = expiration_date + datetime.timedelta(days=term)
        else:
            exp_date = timezone.now() + datetime.timedelta(days=term+1)
        self.services.add(service)
        return self.useroperation_set.create(service_id=service.id, action=1, term=term,
                                      expiration_date=exp_date, info=info)

    def remove_ab_status(self, service, info=''):
        """Убирает статус абонента, принимает комментарий, сохраняет запись в UserOperation"""
        # service = Service.objects.get(id=service_id)
        self.services.remove(service)
        return self.useroperation_set.create(service=service, action=2, info=info)

    def get_exp_date(self, service_id):
        """возвращает дату окончания действия услуги или None"""
        last_operation = self.useroperation_set.filter(
            service_id=service_id).order_by('pk').last()
        return last_operation.expiration_date if last_operation else None

    def active_cities(self):
        return ', '.join(self.services.all().values_list('ru_name', flat=True))
        
    def has_module_perms(self, app_label):
        return True
    
    @property
    def is_staff(self):
        return self.is_admin

    def is_redactor(self):
        try:
            return self.groups.get(name='redaktor')
        except ObjectDoesNotExist:
            return False

    def add_phoundes(self, money):
        self.current_balance += money
        self.save()

    def take_phoundes(self, money):
        self.current_balance -= money
        if self.current_balance < 0:
            from math import fabs
            raise Exception("Not enough money, need yet %s" %
                                                (fabs(self.current_balance)))
        else:
            self.save()

    def get_user_ips(self):
        ip = self.userip_set.all()
        return ip

    def get_ab_op(self):
        return self.useroperation_set.filter(service__name__startswith='base_')

    def get_phones(self):
        phone_list = self.phone_set.all();
        return  phone_list
        
    def get_adv_phones(self):
        adv_phones = set()
        for adv in self.advert_set.all().prefetch_related('phone_set'):
            for phone in adv.phone_set.all():
                adv_phones.add(phone.phone)
        return list(adv_phones)
        
    def mark_phone_as_main(self, phone):
        for ph in self.phone_set.filter(main=True):
            ph.main = False
            ph.save()
        phone.main = True
        phone.save()

    # почтовый модуль
    def send_mail(self, templ_id, day=None, advert=None):
        shape_mail = UserMessage.objects.get(id=templ_id)

        if not self.token:
            self.token = hashlib.sha224(''.join((self.username,
                self.email, str(self.id), 'random')).encode('utf-8')).hexdigest()
            self.save()
        if templ_id == 8: # отправка при регистрации
            ad_message = EmailMessage(
                shape_mail.subject % self.username,
                shape_mail.mail_text % (self.username, 
                                        self.username,
                                        str(self.remember[:2]+'...'+self.remember[-1:]), 
                                        self.token, 
                                        self.token, 
                                        self.token),
                shape_mail.sender, 
                [self.email]
            )
        elif templ_id == 9: # отправка при подачи объявления
            ad_message = EmailMessage(
                shape_mail.subject,
                shape_mail.mail_text % (self.token, self.token, self.token, self.token, self.token),
                shape_mail.sender, 
                [self.email]
            )
        elif templ_id == 10: # отправка при окончании оплаты объявления
            ad_message = EmailMessage(
                shape_mail.subject,
                shape_mail.mail_text % (day,
                                        self.token,
                                        advert.get_photo_preview(),
                                        advert.get_absolute_url(), self.token,
                                        advert.title, advert.price_uah), 
                shape_mail.sender, 
                [self.email]
            )
        elif templ_id == 4: # отправка при отключении базы без посредников
            ad_message = EmailMessage(shape_mail.subject, 
                                      shape_mail.mail_text % (self.token), 
                                      shape_mail.sender, 
                                      [self.email])
        elif templ_id == 11: # отправка при окончании оплаты базы без посредников
            ad_message = EmailMessage(shape_mail.subject,
                                      shape_mail.mail_text % (day, self.token), 
                                      shape_mail.sender, 
                                      [self.email])
        # elif templ_id == 12: # отправка если пользователь давно не обновлял объявления
        #     ad_message = EmailMessage(shape_mail.subject,
        #         shape_mail.mail_text % (self.token), shape_mail.sender, [self.email])
        ad_message.content_subtype = "html"
        ad_message.send(fail_silently=True)

    class Meta:
        ordering = ['username'] 
        verbose_name=u'Пользователь'
        verbose_name_plural = u'Пользователи'


class UserPayment(models.Model):
    """Тут хранятся записи платежей пользователей через liqpay и webmoney"""
    user = models.ForeignKey(UserData, verbose_name=u'Пользователь')
    date = models.DateTimeField(verbose_name=u'Дата оплаты', default=timezone.now)
    service = models.ForeignKey(PaidService, blank=True, null=True)
    annotation = models.CharField(verbose_name=u'Назначение платежа', #на удаление
                                  max_length=100, blank=True) 
    description = models.CharField(verbose_name=u'Описание платежа', default='PAY BASE', 
                                   max_length=100, blank=True)
    amount = models.DecimalField(verbose_name=u'Сумма', max_digits=10, decimal_places=2)
    order_id = models.CharField(verbose_name=u'id заказа', max_length=32, blank=True)
    advert = models.ForeignKey('board.Advert', blank=True, null=True)
    status = models.CharField(verbose_name=u'статус транзакции', max_length=32, blank=True)
    code = models.CharField(verbose_name=u'код ошибки (если есть ошибка)', 
                            max_length=32, blank=True)
    transaction_id = models.CharField(verbose_name=u'id транзакции в системе LiqPay', 
                                      max_length=32, blank=True)
    pay_way = models.CharField(verbose_name=u'способ которым оплатит покупатель', 
                               max_length=32, blank=True)
    sender_phone = models.CharField(verbose_name=u'телефон оплативший заказ', 
                                    max_length=10, blank=True)
    duration = models.IntegerField(verbose_name=u'Продолжитиельность действия', default=0)

    def get_pay_form(self):
        lq = LiqPay(settings.LIQPAY_MERCHANT_ID, settings.LIQPAY_SIGNATURE)
        payment_params = {'version': '3',
                          'amount': str(self.amount),
                          'currency': 'UAH',
                          'description': self.description,
                          'order_id': self.order_id,
                          'result_url': 'http://ci.ua/accounts/profile/',
                          'server_url': 'http://ci.ua/accounts/liqpay/result',
                          'type': 'buy',}
                          # 'sandbox': '1',} # tesst payment
        lq_form = lq.cnb_form(payment_params)
        self.save()
        return lq_form

    def get_webmoney_form(self):
        self.save()
        frm = """<form id='pay_liqpay_form' action='%(url)s' method='POST'>
                 <input type='hidden' name='LMI_PAYMENT_AMOUNT' value='%(amount)s' />
                 <input type='hidden' name='LMI_PAYMENT_DESC' value='%(desc)s' />
                 <input type='hidden' name='LMI_PAYMENT_NO' value='%(pay_no)s' />
                 <input type='hidden' name='LMI_PAYEE_PURSE' value='%(purse)s' />
                 <input type='hidden' name='LMI_SIM_MODE' value='%(sim_mode)s' />
                 <input type='submit' value='%(caption)s'/>
                 </form>""" % {'url': 'https://merchant.webmoney.ru/lmi/payment.asp',
                               'amount': self.amount,
                               'desc': self.description,
                               'pay_no': self.id,
                               'purse': settings.WEBMONEY_PURSE,
                               'sim_mode': 0,
                               'caption': 'pay money'}
        return frm
        
    @staticmethod
    def read_answer(xml):
        #import pdb;pdb.set_trace()
        xml = base64.b64decode(xml)
        return dict(((elt.tag, elt.text) for elt in xee.fromstring(xml)))


class UserIP(models.Model):
    user = models.ManyToManyField(UserData, verbose_name=u'Пользователь')
    ip = models.IPAddressField()


class UserOperation(models.Model):
    """Записи операций пользователей по вкл/откл платных услуг"""
    user = models.ForeignKey(UserData, verbose_name=u'Пользователь')
    action = models.SmallIntegerField(choices=USER_ACTION_CHOICES)
    service = models.ForeignKey(PaidService)
    payment = models.ForeignKey(UserPayment, null=True, blank=True)
    operation = models.SmallIntegerField(null=True, blank=True) #на удаление
    info = models.CharField(max_length=100, blank=True)
    execution_date = models.DateTimeField(default=timezone.now)
    term = models.IntegerField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    advert = models.ForeignKey("board.Advert", blank=True, null=True)

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return self.user.username


class UserMessage(models.Model):
    name = models.CharField(verbose_name=u'Предназначение шаблона письма',
                            max_length=100, blank=True)
    subject = models.TextField(verbose_name=u'Заголовок', max_length=4000)
    mail_text = RichTextField(verbose_name=u'Текст', max_length=4000)
    sender = models.CharField(verbose_name=u'Отправитель', max_length=100, blank=True)
    addressee = models.TextField(verbose_name=u'Получатели', max_length=4000, blank=True)

    def __unicode__(self):
        return self.name
        
        
class UserDataSocial(models.Model):
    user = models.ForeignKey(UserData, blank=True, null=True)
    uid = models.CharField(max_length=100)
    network = models.CharField(max_length=20)
    first_name = models.CharField(max_length=30, blank=True)
    token = models.CharField(max_length=100, blank=True)
    email = models.EmailField()


class UserWalletHistory(models.Model):
    user = models.ForeignKey(UserData)
    deposit = models.OneToOneField(UserPayment, blank=True, null=True)
    withdraw = models.OneToOneField(UserOperation, blank=True, null=True)
    new_sum = models.DecimalField(verbose_name=u'Сумма', max_digits=10, decimal_places=2)
    info = models.CharField(max_length=100)
