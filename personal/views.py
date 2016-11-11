# -*- coding: utf-8 -*-
from realtyboard.settings import WEBMONEY_PURSE, PROJECT_PATH
from decimal import Decimal
from django.conf.urls import url
from django.contrib.auth import authenticate, login as login_django, \
    logout as logout_django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, request
from django.shortcuts import render_to_response, render, redirect
from django.template.context import RequestContext
from django.utils import formats, timezone
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie,\
    requires_csrf_token, csrf_exempt
from hashlib import md5, sha224
from liqpay.liqpay import LiqPay
from operator import itemgetter
from random import randrange
import base64, datetime, json, os, re, uuid, urllib2

from board.forms import FastUserForm
from board.models import Phone, Advert, PaidAdvert, City
from board.views import generate_pass
from personal.models import UserData, UserPayment, UserIP, UserOperation,\
    UserDataSocial, PaidService, ServicePrice, UserWalletHistory, UserMessage
from personal.forms import PaymentReportForm
from realtyboard.settings import LIQPAY_MERCHANT_ID, LIQPAY_SIGNATURE

def email_exists(email):
    if UserData.objects.filter(email=email).exists():
        return True
    return False

def username_exists(username):
    if UserData.objects.filter(username=username).exists():
        return True
    return False

def is_phone_free(phone):
    try:
        ph = Phone.objects.get(phone=phone)
        if ph.owner == None:
            return True
        else:
            return False
    except ObjectDoesNotExist:
        return True

def register(request):
    user = request.user
    if user.is_authenticated():
        return HttpResponseRedirect(reverse('logout'))
    if request.is_ajax():  # проверка наличия логина, почты, телефона в базе
        if request.method == 'POST':
            obj_value = request.POST.get('input_value')
            if request.POST.get('field_name') == 'email':
                try:
                    UserData.objects.get(email=obj_value)
                    return HttpResponse('exists')
                except ObjectDoesNotExist:
                    return HttpResponse('not_exists')
            elif request.POST.get('field_name') == 'username':
                try:
                    UserData.objects.get(username=obj_value)
                    return HttpResponse('exists')
                except ObjectDoesNotExist:
                    return HttpResponse('not_exists')
            elif request.POST.get('field_name') == 'phone':
                if is_phone_free(obj_value):
                    return HttpResponse('not_exists')
                else:
                    return HttpResponse('exists')
        return HttpResponse('unavailable')

    if request.method == 'POST':
        if request.POST['mail'] != '':
            # seems this is a bot
            return redirect(reverse('board-main'))
        else:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            repassword = request.POST.get('repassword')
            first_name = request.POST.get('firstname')
            last_name = request.POST.get('lastname')
            phone = request.POST.get('phone')
            errors = {}

            if len(password) < 5:
                errors['pass_too_short'] = u"Пароль слишком короткий"
            if password == repassword:
                if not email:
                    errors['empty_email'] = u"Поле 'email' обязательно для заполнения"
                elif email_exists(email):
                    errors['email_exists'] = u"Пользователь с таким email уже существует"

                if not username:
                    errors['empty_login'] = u"Поле 'логин' обязательно для заполнения"
                else:
                    username = username.encode('utf-8')
                    if re.match(ur'^[а-яА-Я\w_\.@-]{3,35}$', username) == None:
                        errors['invalid_username'] = u'Некорректные символы в поле "логин", \
                            разрешены буквы, цифры и символы: _ - . @'
                    elif username_exists(username):
                        errors['username_exists'] = u"Пользователь с таким логином уже существует"

                if re.match(r'^0?[1-9][0-9]{8}$', phone) == None:
                    errors['invalid_phone'] = u"Номер телефона обзязателен и должен состоять из 10 цифр"
                elif not is_phone_free(phone):
                    errors['phone_is_busy'] = u"Такой номер уже закреплен за другим пользователем"

                if not errors:
                    user = UserData.objects.create_user(email=email, username=username,
                        first_name=first_name, last_name=last_name, password=password)
                    user.remember = password
                    user.save()
                    ip, create = UserIP.objects.get_or_create(ip=request.META['REMOTE_ADDR'])
                    ip.user.add(user)
                    if phone:
                        phone_obj, a = Phone.objects.get_or_create(phone=phone)
                        user.phone_set.add(phone_obj)
                        phone_obj.main = True
                        phone_obj.save()
                        
                    register_user = authenticate(username=username, password=password)
                    if register_user is not None:
                        if register_user.is_active:
                            login_django(request, register_user)
                            request.user.send_mail(8)
                    return HttpResponseRedirect(reverse('profile'))
                else:
                    return render(request, 'personal_register.html', locals())
            else:
                errors['password_match_error'] = u"Пароли не совпадают."
                return render(request, 'personal_register.html', locals())
    else:
        return render(request, 'personal_register.html', locals())

def login(request):
    csrfContext = RequestContext(request)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                if request.POST.get('remember_me', None):
                    request.session.set_expiry(16000000)
                else:
                    request.session.set_expiry(0)
                login_django(request, user)
                ip, create = UserIP.objects.get_or_create(ip=request.META['REMOTE_ADDR'])
                if create or not UserIP.objects.filter(user__id=user.id).count() :
                    ip.user.add(user)
                return HttpResponseRedirect(reverse('profile'))
            else:
                pass# Return a 'disabled account' error message
        else:
            login_error = u'Неверный логин или пароль'
            return render(request, 'personal_login.html', locals())
    else:
        login_error = False
        return render(request, 'personal_login.html', locals())

def logout(request):
    logout_django(request)
    response = HttpResponseRedirect(reverse('login'))
    response.delete_cookie('zen')
    return response

@login_required
def profile(request):  
    user = request.user
    if user.is_authenticated():
        user_advert_list = Advert.objects.filter(author_id=user.id)
        available_bases = PaidService.objects.filter(name__startswith='base_')
        active_bases = []
        for service in user.services.all():
            expiration_date = user.get_exp_date(service.id)
            if expiration_date == None or expiration_date < datetime.date.today():
                user.remove_ab_status(service, info=u"Просрочена дата конца срока абонентства")
            else:
                active_bases.append({'service': service, 'exp_date': expiration_date})
        if request.method == 'GET':
            list_type = request.GET.get('list')
            if list_type == 'inactive':
                #import pdb; pdb.set_trace()
                advert_list = user_advert_list.filter(is_active=False)
            elif list_type == 'paid':
                advert_list = user_advert_list.filter(paidadvert__isnull=False)
                for adv in advert_list:
                    adv.services = adv.active_services()
            elif list_type == 'favorite':
                advert_list = user.favorite_adv.all()
            elif list_type == 'deleted':
                advert_list = user_advert_list.filter(adverttodelete__isnull=False)
                for adv in advert_list:
                    if adv.adverttodelete.date_of_del < (
                            datetime.date.today() - datetime.timedelta(days=7)):
                        adv.delete();
            elif list_type == 'vip':
                advert_list_vip = []
                advert_list = user_advert_list.filter(is_active=True)
                for adv in advert_list:
                    if "adv_vip" in adv.active_services():
                        advert_list_vip.append(adv)
                    else: continue
                advert_list = []
                advert_list = advert_list_vip
                advert_list_vip = advert_list
                for adv in advert_list:
                    adv.services = adv.active_services()
            elif list_type == 'top':
                advert_list_vip = []
                advert_list = user_advert_list.filter(is_active=True)
                for adv in advert_list:
                    if "adv_top" in adv.active_services():
                        advert_list_vip.append(adv)
                    else: continue
                advert_list = []
                advert_list = advert_list_vip
                advert_list_vip = advert_list
                for adv in advert_list:
                    adv.services = adv.active_services()
            else:
                advert_list = user_advert_list.filter(is_active=True)
                for adv in advert_list:
                    adv.services = adv.active_services()
        return render(request, 'personal_profile.html', locals())
    else:
        return HttpResponseRedirect('/accounts/login/')


def get_pay(request):
    if request.POST['purpose'] == 'balance':
        service = None
    else:
        if request.POST['purpose'].isdigit():
            service = PaidService.objects.get(id=request.POST['purpose'])
        else:
            service = PaidService.objects.get(name=request.POST['purpose'])
    adv_id = int(request.POST['obj_id']) if request.POST.get('obj_id', None) else None
    payments = UserPayment(order_id=uuid.uuid4().hex,
                           amount=request.POST.get('amount'),
                           pay_way=request.POST.get('pay_way'),
                           user=request.user,
                           date=timezone.now(),
                           annotation='',
                           duration=get_pay_duration(
                                request.POST['amount'], service.name) if service else 0,
                           status='start',
                           service=service,
                           advert_id=adv_id,
                           description=service.name if service else 'balance',)
    if request.POST['pay_way'] == 'liqpay':
        frm = payments.get_pay_form()
    elif request.POST['pay_way'] == 'webmoney':
        frm = payments.get_webmoney_form()
    result = {"frm_pay": frm}
    return HttpResponse(json.dumps(result))

@csrf_exempt
def liqpay(request):
    pay_result = json.loads(base64.decodestring(request.POST['data']))
    lq = LiqPay(LIQPAY_MERCHANT_ID, LIQPAY_SIGNATURE)
    signature = lq.str_to_sign(
        LIQPAY_SIGNATURE + request.POST['data'] + LIQPAY_SIGNATURE
    )
    payment = UserPayment.objects.get(order_id=pay_result['order_id'])
    payment.status = pay_result['status']
    payment.transaction_id = pay_result['transaction_id']
    if 'sender_phone' in pay_result:
        payment.sender_phone = pay_result['sender_phone'][-10:]
    if request.POST['signature'] != signature:
        payment.status = payment.status + ' signature missmatch'
    elif payment.status == 'success':
        user = payment.user
        if payment.service:
            if 'base_' in payment.service.name:
                payment.useroperation_set.add(user.set_ab_status(
                    payment.service, payment.duration, info=u'оплата liqpay'))
            elif 'adv_' in payment.service.name:
                payment.useroperation_set.add(payment.advert.activate_service(
                    service=payment.service, term=payment.duration))
        elif 'balance' in payment.description:
            user.current_balance += payment.amount
            user.save()
            UserWalletHistory.objects.create(user=user, new_sum=user.current_balance,
                                             deposit=payment, info=payment.pay_way)
    elif payment.status == 'sandbox':
        payment.annotation = 'test payment'
    payment.save()
    response = HttpResponse('ok')
    return response

@csrf_exempt
def webmoney_result(request):
    if request.method == 'POST':
        data = request.POST
        payment = UserPayment.objects.get(id=int(request.POST['LMI_PAYMENT_NO']))
        if request.POST.get('LMI_PREREQUEST', None) == '1':
            if request.POST.get('LMI_PAYEE_PURSE') == WEBMONEY_PURSE:
                    payment.status = 'prerequest'
                    response = HttpResponse("YES")
                    if payment.amount != Decimal(request.POST['LMI_PAYMENT_AMOUNT']):
                        response = HttpResponse('incorrect payment amount')
                    payment.save()
                    response['Access-Control-Allow-Origin'] = 'https://merchant.webmoney.ru' 
                    response['Content-Type'] = 'text/html'
                    return response
            response = HttpResponse('Wrong data')
            response['Access-Control-Allow-Origin'] = 'https://merchant.webmoney.ru' 
            response['Content-Type'] = 'text/html'
            return response
        else:
            if request.POST.get('LMI_SYS_INVS_NO'):
                user = payment.user
                payment.status = 'success'
                payment.save()
                if payment.service:
                    if 'base_' in payment.service.name:
                        payment.useroperation_set.add(user.set_ab_status(
                            payment.service, payment.duration, info=u'оплата webmoney'))
                    elif 'adv_' in payment.service.name:
                        payment.useroperation_set.add(payment.advert.activate_service(
                            service=payment.service, term=payment.duration))
                elif 'balance' in payment.description:
                    user.current_balance += payment.amount
                    user.save()
                    UserWalletHistory.objects.create(user=user, new_sum=user.current_balance,
                                                    deposit=payment, info=payment.pay_way)
            else:
                payment.status = 'failed on webmoney side'
                payment.save()
            response = HttpResponse('YES')
            response['Access-Control-Allow-Origin'] = 'https://merchant.webmoney.ru' 
            response['Content-Type'] = 'text/html'
            return response
    else:    
        response = HttpResponse('not post query')
        response['Access-Control-Allow-Origin'] = 'https://merchant.webmoney.ru' 
        response['Content-Type'] = 'text/html'
        return response  

def get_pay_duration(amount, service_name):
    try:
        price = ServicePrice.objects.get(kind=service_name, price=int(amount))
        return price.days
    except ServicePrice.DoesNotExist:
        return 0
        
@login_required
def profile_settings(request):
    user = request.user

    if request.is_ajax():
        """проверка наличия логина, почты, телефона в базе налету"""
        if request.method == 'POST':
            obj_value = request.POST.get('input_value')
            if request.POST.get('field_name') == 'email':
                try:
                    UserData.objects.get(email=obj_value)
                    return HttpResponse('exists')
                except ObjectDoesNotExist:
                    return HttpResponse('not_exists')
            elif request.POST.get('field_name') == 'username':
                try:
                    UserData.objects.get(username=obj_value)
                    return HttpResponse('exists')
                except ObjectDoesNotExist:
                    return HttpResponse('not_exists')
            elif request.POST.get('field_name') == 'phone':
                if is_phone_free(obj_value):
                    return HttpResponse('not_exists')
                else:
                    return HttpResponse('exists')
        return HttpResponse('unavailable')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        phone = request.POST.get('phone')
        main_phone = request.POST.get('main_phone')
        errors = {}
        current_phones = user.phone_set.all()
        new_main_phone = request.POST.get('main_phone', None)

        if password == repassword:
            if email == user.email:
                errors['same_email'] = u"Вы не изменили почту"
            elif email_exists(email):
                errors['email_exists'] = u"Пользователь с таким email уже существует!"

            if phone:
                same_phone = False
                for phone1 in current_phones: # проверка не ввел ли пользователь
                    if int(phone) == int(phone1.phone):             #один из своих телефонов
                        same_phone = True
                if same_phone:
                    errors['same_phone'] = u"Этот номер телефона уже закреплен за вами"
                else:
                    if re.match(r'^0?[1-9][0-9]{8}$', phone) == None:
                        errors['invalid_phone'] = u"Номер телефона должен состоять из 10 цифр"
                    elif not is_phone_free(phone):
                        errors['phone_is_busy'] = u"Такой номер уже закреплен за другим пользователем"

            if last_name != '' and last_name == user.last_name:
                errors['same_last_name'] = u"Вы не изменили фамилию"

            if first_name != '' and first_name == user.first_name:
                errors['same_first_name'] = u"Вы не изменили имя"

            if not errors:
                if email:
                    user.email = email
                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                if password:
                    user.set_password(password)
                    remember = password
                user.save()
                if phone:
                    phone_obj, a = Phone.objects.get_or_create(phone=phone)
                    user.phone_set.add(phone_obj)
                    if new_main_phone == '0':
                        user.mark_phone_as_main(phone_obj)
                for pho in current_phones:
                    if request.POST.get('del_'+str(pho)):
                        phone_to_del = user.phone_set.get(phone=str(pho))
                        user.phone_set.remove(phone_to_del)
                    if new_main_phone and int(new_main_phone) == pho.phone:
                        user.mark_phone_as_main(pho)
                return HttpResponseRedirect(reverse('profile'))
            else:
                return render(request, 'personal_settings.html', locals())
        else:
            errors['password_match_error'] = u"Пароли не совпадают."
            return render(request, 'personal_settings.html', locals())
    else: #GET
        return render(request, 'personal_settings.html', locals())

def ab_status(request):
    if request.is_ajax():
        if request.method == 'POST':
            data = request.POST
            service = PaidService.objects.get(id=data['service_id'])
            user_obj = UserData.objects.get(pk=data['user_id'])
            if data['action'] == 'set':
                user_oper_obj = user_obj.set_ab_status(
                    service, int(data['term']), info=data['info'])
            elif data['action'] == 'unset':
                user_oper_obj = user_obj.remove_ab_status(service)
            else:
                return HttpResponse(u'Ошибка. Не выполнено никаких действий')
            return render(request, 'admin/personal/userdata/one_user_operation.html',
                          {'item': user_oper_obj})
        return HttpResponse('some error in personal.views')

def pay_from_balance(request):
    if request.is_ajax() and request.method == 'POST':
        user = request.user
        service = PaidService.objects.get(name=request.POST['purpose'])
        response = {'status': 'success'}
        term = get_pay_duration(request.POST['amount'], request.POST['purpose'])
        if term > 0:
            after_pay_balance = user.current_balance - int(request.POST['amount'])
            if after_pay_balance >= 0:
                advert = None
                if 'base_' in service.name:
                    user_operation = user.set_ab_status(service=service, term=term, 
                                                       info=u'с баланса')
                    response['new_balance'] = int(user.current_balance)
                    response['message'] = u'Доступ к базе включен'
                    response['exp_date'] = formats.date_format(user_operation.expiration_date)
                    response['service_ru_name'] = service.ru_name
                elif 'adv_' in service.name:
                    advert = Advert.objects.get(id=int(request.POST['obj_id']))
                    user_operation = advert.activate_service(service=service, term=term,
                                                             info=u"с баланса")
                    success_msgs = {
                        'adv_top': u'Объявление №%s теперь будет отображаться в TOP блоке' % advert.id,
                        'adv_highlight': u'Объявление №%s теперь будет выделенным' % advert.id,
                        'adv_vip': u'Объявление №%s теперь будет отображаться в VIP блоке' % advert.id,
                        'adv_auto_up': u'У объявления №%s будет автоматически обновляться дата' % advert.id,
                    }
                    response['message'] = success_msgs[request.POST['purpose']]
                    print user_operation.expiration_date.__class__
                    response['term'] = (user_operation.expiration_date - datetime.date.today()).days
                if user_operation:
                    user.current_balance = after_pay_balance
                    user.save()
                    user.userwallethistory_set.create(
                        new_sum=after_pay_balance,
                        withdraw=user_operation,
                        info=service.name+(", adv_id %s" % advert.id if advert else '')
                    )
            else:
                response['status'] = 'error'
                response['message'] = u"""Недостаточно средств на балансе. Пополните
                    баланс, или выберите другой способ оплаты"""
        else:
            response['status'] = 'error'
            response['message'] = u"""Неверная сумма оплаты, повторите попытку, 
                или обратитесь в техподдержку"""
        return HttpResponse(json.dumps(response))


def user_question(request):
    if request.is_ajax() and request.method == 'POST':
        if request.user.is_authenticated():
            mail_text = (u"Пользователь: " + request.user.username.encode('utf-8')
                         + u'\nEmail пользователя: ' + request.user.email
                         + u"\nСпрашивает: "
                         + request.POST['question_text'])
        else:
            mail_text = u"Прохожий спрашивает: %s \n\nEmail для ответа: %s" % (
                request.POST['question_text'], request.POST['email'])
        try:
            send_mail(request.POST.get('title', 'USER QUESTION'), mail_text, 
                'support@ci.ua', ['centrinform@mail.ru'], fail_silently=False)
        except:
            return HttpResponse(u'Сервис временно не доступен.', status=500)
        return HttpResponse(u'Сообщение отправлено.')
    return HttpResponse(u'Ошибка неверный запрос.')

            
def admin_ch_user_pass(request):
    if request.is_ajax():
        if request.method == 'POST':
            if request.user.is_admin:
                new_pass = request.POST.get('login').encode('utf-8')
                ch_user = UserData.objects.get(username=request.POST.get('login'))
                ch_user.set_password(request.POST.get('pdata'))
                ch_user.remember = request.POST.get('pdata')
                ch_user.save()
                return HttpResponse(u'Пароль изменен')
    return HttpResponse(u'Ошибка! Пароль не изменен')

def adm_send_mail(request):
    if request.is_ajax():
        if request.method == 'POST':
            if request.user.is_admin:
                subject = request.POST.get('subject').encode('utf-8')
                mail_text = request.POST.get('mail_text').encode('utf-8')
                mail_to = request.POST.get('mail_to').encode('utf-8')
                try:
                    send_mail(subject, mail_text, 'noreply@ci.ua', [mail_to], fail_silently=False)
                except:
                    return HttpResponse(u'Ошибка. Почта не пошла')
                return HttpResponse(u'Письмо отправлено.')
    return HttpResponse(u'Ошибка, неверный запрос!')

def adm_add_phone(request):
    message = u'Видимо у вас нет прав доступа'
    if request.is_ajax():
        if request.method == 'POST':
            if request.user.is_admin:
                phone = int(request.POST.get('phone'))
                ch_user = UserData.objects.get(id=int(request.POST.get('id')))
                phone_obj, created = Phone.objects.get_or_create(phone=phone)
                if phone_obj.owner == None:
                    ch_user.phone_set.add(phone_obj)
                    phone_obj.save()
                    message = u'<li>0' + str(phone_obj.phone) + '</li>'
                else:
                    message = u'<li class="busy-phone">Этот телефон уже закреплен за пользователем!</li>'
    return HttpResponse(message)

def adm_change_comment(request):
    if request.is_ajax():
        if request.method == 'POST':
            if request.user.is_admin:
                notification = UserOperation.objects.get(id=request.POST.get('id'))
                notification.info = request.POST.get('comment')
                notification.save()
                return HttpResponse(notification.info)
    return HttpResponse(u'Неверный запрос!')
    
def payment_report(request):
    if request.method == 'POST':
        form = PaymentReportForm(request.POST)
        if form.is_valid():
            message = (form.cleaned_data['payment_purpose']
                + u"\nСпособ оплаты: " +  form.cleaned_data['payment_case']
                + u"\nНомер чека: " + form.cleaned_data['check_code']
                + u"\nФИО, организация: " + form.cleaned_data['fio_company']
                + u"\nЛогин: " + form.cleaned_data['username']
                + u"\nПочта: " + form.cleaned_data['user_email']
                + u"\nТелефон: " + form.cleaned_data['user_phone']
                + u"\nСумма: " + form.cleaned_data['sum_of_payment']
                + u"\nДата оплаты: " + form.cleaned_data['date_of_payment'])
            try:
                send_mail(form.cleaned_data['payment_purpose'], message, 'noreply@ci.ua', 
                        ['centrinform@mail.ru'], fail_silently=False)
            except:
                return render(request, 'personal_payment_report.html', {'message': 
                        u'Ошибка отправки сообщения! Попробуйте повторить еще раз, \
                        или сообщите нам об оплате по телефону.', 'form': form})
            return render(request, 'message.html', {'message': u'Сообщение отправлено. \
                    Оно будет обработано в ближайшее время. Если ваш запрос требует \
                    немедленной обработки, то лучше уведомить нас об этом по одному из \
                    телефонов техподдерржки.'})
        return render(request, 'personal_payment_report.html', {'form': form})
    else:
        form = PaymentReportForm(req=request)
        return render(request, 'personal_payment_report.html', {'form': form})
        
@csrf_exempt
def ulogin(request):
    """ network - соц. сеть, через которую авторизовался пользователь
    identity - уникальная строка определяющая конкретного пользователя соц. сети
    first_name - имя пользователя, uuid - uuid пользователя в соцсети"""
    if request.method == 'POST' and request.POST.get('token', None):
        social_data = json.loads(urllib2.urlopen(
            'http://ulogin.ru/token.php?token=%s&host=ci.ua'
            % request.POST['token']).read())
        social_obj, create = UserDataSocial.objects.get_or_create(uid=social_data['uid'], 
            network=social_data['network'])
        if social_obj.user:
            social_obj.user.backend = 'django.contrib.auth.backends.ModelBackend'
            login_django(request, social_obj.user)
            return HttpResponseRedirect(reverse('profile'))
        else:
            social_obj.token = sha224(''.join((social_obj.network,
                social_obj.uid, 'mysecretkey'))).hexdigest()
            social_obj.first_name = social_data['first_name']
            social_obj.save()
            return HttpResponseRedirect(reverse('social_new', kwargs={'token': social_obj.token}))
            
            
def social_new(request, token):
    social_obj = UserDataSocial.objects.get(token=token)
    context = {'network': social_obj.network}
    if request.method == 'POST':
        context['email'] = request.POST['email']
        mail_text = u"""Здравствуйте, вы получили это письмо, потому что ваша почта была
            использована для входа на сайт http://ci.ua через социальные сети. Чтобы
            подтвердить свою почту просто перейдите по ссылке 
            http://ci.ua/accounts/social/mail_confirm/%s""" % social_obj.token
        try:
            send_mail(u"Подтверждение почты на ci.ua", mail_text, 'noreply@ci.ua',
                [request.POST['email'],], fail_silently=False)
            social_obj.email = request.POST['email']
            social_obj.save()
        except:
            context['error'] = 1
            return render(request, 'social_reg.html', context)
        context['message'] = u"Проверьте свою почту и перейдите по указанной в письме ссылке."
        return render(request, 'message.html', context)
    else:
        return render(request, 'social_reg.html', context)
        
        
def social_mail_confirm(request, token):
    try:
        social_obj = UserDataSocial.objects.get(token=token)
        user_obj = UserData.objects.get(email=social_obj.email)
    except UserDataSocial.DoesNotExist:
        return render(request, 'message.html', {'message': u"Время действия ссылки истекло."})
    except UserData.DoesNotExist:
        if social_obj.first_name:
            first_name = social_obj.first_name
        else:
            b = re.match(r'\w+', social_obj.email)
            first_name = b[0]
        user_pass = generate_pass()
        user_obj = UserData.objects.create_user(
            email=social_obj.email,
            username=social_obj.email,
            first_name=first_name,
            password=user_pass
        )
        mail_text = u"""Здравствуйте, вы успешно зарегистрировались на сайте ci.ua.
            Ваши данные для входа на сайт:
            Ваш логин: %s
            Ваш пароль: %s""" % (user_obj.username, user_pass)
        send_mail(u"Вы зарегистрировались на сайте ci.ua", mail_text, 'noreply@ci.ua',
            [user_obj.email,], fail_silently=False)
    social_obj.user = user_obj
    social_obj.token = ''
    social_obj.save()
    user_obj.backend = 'django.contrib.auth.backends.ModelBackend'
    login_django(request, user_obj)
    return HttpResponseRedirect(reverse('profile'))    
    
def get_abonent_groups():
    ab_groups = Group.objects.filter(name__startswith='base_')
    ab_cities = City.objects.filter(slug__in=[sl.replace('base_', '') for sl in\
        ab_groups.values_list('name', flat=True)]).order_by('slug')
    ab_groups_list = []
    for i, g in enumerate(ab_groups):
        ab_groups_list.append(
            {'id': g.id, 'name': g.name, 'city_name': ab_cities[i].name})
    ab_groups_list = sorted(ab_groups_list, key=itemgetter('city_name'))
    return ab_groups_list   
    
def get_pay_btns(request):
    if request.is_ajax() and request.method == 'POST':
        return render( request, 'personal/templatetags/pay_btns.html', {
            'prices': ServicePrice.objects.filter(kind=request.POST['purpose'])})
        
def get_base_prices(request):
    if request.is_ajax() and request.method == 'POST':
        available_bases = PaidService.objects.filter(
            name__startswith='base_').prefetch_related('prices')
        prices = {}
        for base in available_bases:
            prices[base.id] = {}
            for price in base.prices.all().order_by('days'):
                prices[base.id][price.days] = model_to_dict(price)
        return HttpResponse(json.dumps(prices))

def profile_mail(request, token, send_param):
    try:
        user = UserData.objects.get(token=token)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login_django(request, user)
        if send_param == 'oplata':
            return HttpResponseRedirect(reverse('oplata'))
        elif send_param == 'profile':
            return HttpResponseRedirect(reverse('profile'))
        elif send_param == 'add':
            return HttpResponseRedirect(reverse('property_add'))
    except UserData.DoesNotExist:
        # Ссылка устарела
        return HttpResponseRedirect(reverse('login'))
