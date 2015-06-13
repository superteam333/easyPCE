# Scraper of DA's from Princeton registrar website. 
# Written by John Whelchel for COS 333 Final Project
# Based on code written by Alex Ogier
# Spring 2013
#
# Comment out unwanted Semesters!!!
#
#!/usr/bin/env python
"""
Python routines for scraping data from Princeton's registrar.
by Alex Ogier

If run as a python script, the module will dump information on all the courses available
on the registrar website as a JSON format.

Check out LIST_URL to adjust what courses are scraped.

Useful functions are scrape_page() and scrape_all().
"""

from datetime import datetime
import json
import re
import sqlite3
import sys
import os
import urllib2
from BeautifulSoup import BeautifulSoup
from collections import OrderedDict
import itertools
import StringIO
import operator

sys.path.append('/srv/www/myapp/')
sys.path.append('/srv/www/myapp/pce')
from myapp import settings
from django.core.management import setup_environ
setup_environ(settings)
from models import *



termss = dict()
#termss['Fall_2006-2007']=1072
#termss['Fall_2007-2008']=1082
#termss['Fall_2008-2009']=1092
#termss['Fall_2009-2010']=1102
#termss['Fall_2010-2011']=1112
#termss['Fall_2011-2012']=1122
#termss['Fall_2012-2013']=1132
#termss['Fall_2013-2014']=1142
termss['Fall_2014-2015']=1152
#termss['Spring_2006-2007']=1074
#termss['Spring_2007-2008']=1084
#termss['Spring_2008-2009']=1094
#termss['Spring_2009-2010']=1104
#termss['Spring_2010-2011']=1114
#termss['Spring_2011-2012']=1124
#termss['Spring_2012-2013']=1134
#termss['Spring_2013-2014']=1144


TERM_CODE = 'Fall_2014-2015'
URL_PREFIX = "http://registrar.princeton.edu/course-offerings/"
LIST_URL = URL_PREFIX + "search_results.xml?term={term}"
COURSE_URL = URL_PREFIX + "course_details.xml?courseid={courseid}&term={term}"

COURSE_URL_REGEX = re.compile(r'course_details.*courseid=(?P<id>\d+)')
PROF_URL_REGEX = re.compile(r'dirinfo\.xml\?uid=(?P<id>\d+)')
LISTING_REGEX = re.compile(r'(?P<dept>[A-Z]{3})\s+(?P<num>\w{2,4})')

def get_DAs(search_page):
  global TERM_CODE
  "Grep through the document for a list of course ids."
  soup = BeautifulSoup(search_page)
  links = soup('a', href=COURSE_URL_REGEX)

  for i in links:
#    print "Link is " + str(i)
#    print type(i.u.contents[0].string)
    courseID = clean(i.u.contents[0].string).split()
#    print "CourseID is " + str(courseID)
    try:
      d = Department.objects.get(dept=courseID[0])
      print d
      courseNum = CourseNum.objects.get(dept=d, number=courseID[1])
      print "CourseNum is " + str(courseNum)
      try:
        course = Course.objects.get(coursenum__id=courseNum.id, semester=TERM_CODE.split("_")[0], year=TERM_CODE[-9:])
        da= clean(i.parent.parent.contents[7].string)
        print str(course) + " " + str(da)
        print " "
        course.da=da
        course.save()
      except:
        print courseNum
        print "YO GETTING COURSE FAILED."
    except Department.DoesNotExist:
      print "dept fail"
    except:
      print "YO GETTING COURSENUM FAILED."

def clean(str):
  "Return a string with leading and trailing whitespace gone and all other whitespace condensed to a single space."
  return re.sub('\s+', ' ', str.strip())

def scrape_all(term):
  """
  Return an iterator over all courses listed on the registrar's site.
  
  Which courses are retrieved are governed by the globals at the top of this module,
  most importantly LIST_URL and TERM_CODE.

  To be robust in case the registrar breaks a small subset of courses, we trap
  all exceptions and log them to stdout so that the rest of the program can continue.
  """
  print term
  print termss[term]
  print LIST_URL.format(term=termss[term])
  search_page = urllib2.urlopen(LIST_URL.format(term=termss[term]))

  get_DAs(search_page)


if __name__ == "__main__":
  
  if len(sys.argv) > 1:
    TERM_CODE = str(sys.argv[1])
  for key in termss:
    TERM_CODE = key
    scrape_all(TERM_CODE)

