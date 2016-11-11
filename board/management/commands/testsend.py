# -*- coding: utf-8 -*-
import os
from django.core.management.base import BaseCommand
import sys
from chilkat import chilkat
from realtyboard.settings import MEDIA_ROOT

class Command(BaseCommand):
    proxy_list = []

    def handle(self, *args, **options):
        mailman = chilkat.CkMailMan()

        success = mailman.UnlockComponent("30-day trial")
        if (success != True):
            print(mailman.lastErrorText())
            sys.exit()
        # f = open(os.path.join(MEDIA_ROOT, 'proxy', 'fine_all_proxy.txt'))
        # proxy_list = f.readlines()
        # for i in proxy_list[:3]:
        # mailman.put_HttpProxyHostname('227.149.151.178.triolan.net')
        # mailman.put_HttpProxyPort(80)


        mailman.put_SmtpHost("227.149.151.178.triolan.net")
        mailman.put_SmtpPort(80)


        mailman.put_SmtpUsername("")
        mailman.put_SmtpPassword("")


        email = chilkat.CkEmail()

        email.put_Subject("Hello Python!")
        email.put_Body("Hello world!")
        email.put_From("Chilkat Support <noreply@ci.ua>")
        success = email.AddTo("Chilkat Admin", "andreyhomenko92@mail.ru")
        success = mailman.SendEmail(email)
        if (success != True):
            print(mailman.lastErrorText())
            sys.exit()
        success = mailman.CloseSmtpConnection()
        if (success != True):
            print("Connection to SMTP server not closed cleanly.")
        print("Mail Sent!")
