# -*- coding: utf-8 -*-
from personal.models import UserData
from realtyboard.settings import MEDIA_ROOT



def send_mor():
	email_2014=UserData.objects.filter(creation_date__year=2014).values_list('email', flat=True)
	f=open('%s/proxy/email_2014.txt ' % MEDIA_ROOT, 'w')
	for text in email_2014:
		f.write(text.encode('utf-8')+"\n")
	f.close()
