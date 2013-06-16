# This file is used to calculate avg and bestprof for all courses.
# Really shouldn't be needed anymore since calculations done in .save()

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

coursenums = CourseNum.objects.all()
for c in coursenums:
#    print "trying coursenum:"
#    print c
#    if c.avg:
#        print "average exists"
#        print c.avg
#    print "trying to save:"
    c.save()
#    print "avg is now:"
    if c.avg:
        pass
#        print c.avg
    else:
        print "Course still doesn't have average!!"
        print c
#        courses = Course.objects.filter(coursenum=c)
#    print "trying to find profs:"
    profs = Professor.objects.filter(coursenum=c)
    if profs:
        pass
#        for p in profs:
#            print p
    else:
        print "Course still doesn't have best prof!!"
        print c
    print ""
