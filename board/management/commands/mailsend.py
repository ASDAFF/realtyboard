# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from realtyboard.settings import MEDIA_ROOT
from personal.models import UserData
import os, random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class Command(BaseCommand):

    def handle(self, *args, **options):
        emails = UserData.objects.exclude(email__endswith='@urealty.in.ua').order_by().values_list('email','first_name').distinct()
        senders_lst = []
        i = 3
        while i < 53:
            sender = 'centrinform{}@mail.ru'.format(i)
            senders_lst.append(sender)
            i += 1
        smtpserver = 'smtp.mail.ru'
        smtpport = 587
        password = 'ImM7XBCe'

        sender = random.choice(senders_lst)
        separator = sender.find("@")
        login = sender[:separator]
        receiver = "andreyhomenko91@gmail.com"
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = "Начало рассылки"
        msgRoot['From'] = sender
        msgRoot['To'] = receiver
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        notification = "Рассылка началась!"
        text = MIMEText(notification, 'plain', 'utf-8')
        msgRoot.attach(text)
        mail = smtplib.SMTP(smtpserver, smtpport)
        mail.ehlo()
        mail.starttls()
        mail.login(login, password)
        mail.sendmail(sender, receiver, msgRoot.as_string())
        mail.quit()

        sent = 0
        for item in ["andreyhomenko91@gmail.com",'megoloman@ukr.net']:
            try:
                user_name = "Олег"
                # emails[item][1].encode('utf-8')
                sender = random.choice(senders_lst)
                separator = sender.find("@")
                login = sender[:separator]
                receiver = item
                # emails[item][0]
                msgRoot = MIMEMultipart('related')
                msgRoot['Subject'] = "Приглашение на бизнес-тренинги в Харькове"
                msgRoot['From'] = sender
                msgRoot['To'] = receiver
                msgAlternative = MIMEMultipart('alternative')
                msgRoot.attach(msgAlternative)
                file = open(os.path.join(MEDIA_ROOT, 'delivery', 'message.html'))
                html_content = "Здравствуйте, {}!".format(user_name) + file.read()
                html = MIMEText(html_content, 'html', 'utf-8')
                fp = open(os.path.join(MEDIA_ROOT, 'delivery', 'message.jpg'), 'rb')
                msgImage = MIMEImage(fp.read())
                fp.close()
                msgImage.add_header('Content-ID', '<image1>')
                msgRoot.attach(msgImage)
                msgRoot.attach(html)
                mail = smtplib.SMTP(smtpserver, smtpport)
                mail.ehlo()
                mail.starttls()
                mail.login(login, password)
                mail.sendmail(sender, receiver, msgRoot.as_string())
                mail.quit()
                sent += 1
                sleep(3)
            except: continue

        sender = random.choice(senders_lst)
        separator = sender.find("@")
        login = sender[:separator]
        receiver = "andreyhomenko91@gmail.com"
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = "Конец рассылки"
        msgRoot['From'] = sender
        msgRoot['To'] = receiver
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        notification = "Рассылка окончилась! Количество отправленный писем - {}".format(sent)
        text = MIMEText(notification, 'plain', 'utf-8')
        msgRoot.attach(text)
        mail = smtplib.SMTP(smtpserver, smtpport)
        mail.ehlo()
        mail.starttls()
        mail.login(login, password)
        mail.sendmail(sender, receiver, msgRoot.as_string())
        mail.quit()


