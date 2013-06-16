import argparse
from bs4 import BeautifulSoup
from bs4 import Tag
from collections import OrderedDict
import itertools
import json
import os
import re
import StringIO
#import nltk
import operator
import sys
sys.path.append('/srv/www/myapp/')
from myapp import settings
from django.core.management import setup_environ
setup_environ(settings)
from models import *

def readfile(filename):
    contents = None
    with open(filename, 'r') as f:
		contents = f.read()
    return contents

def soupfile(filename):
	html=readfile(filename)
	return BeautifulSoup(html)

bs = soupfile("dep-info.html")
names = [ node.previousSibling.string.strip() for node in bs.findAll('br')]
acronyms= [node.string for node in bs.findAll('a')]

length = len(names)
print length
print acronyms
for i in range(length):
	try:
		dept = Department.objects.get(dept=str(acronyms[i]))
	except Exception:
		dept = None
	if dept is not None:
		dept.name = str(names[i])
		dept.save()
	
