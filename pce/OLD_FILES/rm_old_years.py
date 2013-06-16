import argparse
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

for cn in coursenums:
    print ""
    print unicode(cn.dept) + cn.number
    print ""
    instances = Course.objects.filter(coursenum=cn, year='2007-2008')
    for i in instances:
        print i
        print i.year
