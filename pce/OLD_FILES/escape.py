import os
import re
import sys
sys.path.append('/srv/www/myapp/')
from myapp import settings
from django.core.management import setup_environ
setup_environ(settings)
from models import *
import HTMLParser

hp = HTMLParser.HTMLParser()

needfix = Course.objects.filter(title__icontains="&")
#for i in needfix:
#	print hp.unescape(i.title)

#print hp.unescape("<i>hi</i>")
s = "<i>a</i>"
pattern = re.compile(r'<.*?>')
print pattern.sub('', s)
