#!/usr/bin/env python
"""
Modified by John Whelchel for COS333 
Spring 2013

Used to rip relevant HTML data from registrar for future parsing, specifically
to get course load data.
"""





"""
OLD HEADER

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

# Terms to get info from

termss = dict()

#termss['Fall_2006-2007']=1072
#termss['Fall_2007-2008']=1082
termss['Fall_2008-2009']=1092
termss['Fall_2009-2010']=1102
termss['Fall_2010-2011']=1112
termss['Fall_2011-2012']=1122
termss['Fall_2012-2013']=1132
termss['Fall_2013-2014']=1142
#termss['Fall_2014-2015']=1152
#termss['Spring_2006-2007']=1074
termss['Spring_2007-2008']=1084
termss['Spring_2008-2009']=1094
termss['Spring_2009-2010']=1104
termss['Spring_2010-2011']=1114
termss['Spring_2011-2012']=1124
termss['Spring_2012-2013']=1134
#termss['Spring_2013-2014']=1144


#URL and regular expression globals

URL_PREFIX = "http://registrar.princeton.edu/course-offerings/"
LIST_URL = URL_PREFIX + "search_results.xml?term={term}"
COURSE_URL = URL_PREFIX + "course_details.xml?courseid={courseid}&term={term}"

# This is where the scraped HTML will be saved.
HTML_DIRECTORY = "/srv/www/myapp/easypce_datatools/registrar_scrape/DATA/LOAD_DATA/"

COURSE_URL_REGEX = re.compile(r'courseid=(?P<id>\d+)')
LISTING_REGEX = re.compile(r'(?P<dept>[A-Z]{3})\s+(?P<num>\w{2,4})')




# Gets list of all courses by term from large page.
def get_course_list(search_page):
  "Grep through the document for a list of course ids."
  soup = BeautifulSoup(search_page)
  links = soup('a', href=COURSE_URL_REGEX)
  courseids = [COURSE_URL_REGEX.search(a['href']).group('id') for a in links]
  return courseids


# Gets course listings (i.e. COS126)
def get_course_listings(soup):
  "Return a list of {dept, number} dicts under which the course is listed."
  listings = soup('strong')[1].string
  return [{'dept': match.group('dept'), 'number': match.group('num')} for match in LISTING_REGEX.finditer(listings)]

# Saves the relevant HTML for each course.
def save_html(id, term):
  page = urllib2.urlopen(COURSE_URL.format(term=term, courseid=id))
  soup = BeautifulSoup(page).find('div', id='contentcontainer')
  course = {}
  course['listings'] = get_course_listings(soup)
  name = getfilename(course, term)
  try:
    fd = open(HTML_DIRECTORY + name, 'w')
    fd.write(str(soup))
    fd.close()
    print "Succesfully saved file %s \n" % name
  except Exception as e:
    print "Error occured trying to write and save file %s" % name
    print "Exception give was %s" % e
    print ""


def scrape_all(term=""):
  """
  Return an iterator over all courses listed on the registrar's site.
  
  Which courses are retrieved are governed by the globals at the top of this module,
  most importantly LIST_URL and TERM_CODE.

  To be robust in case the registrar breaks a small subset of courses, we trap
  all exceptions and log them to stdout so that the rest of the program can continue.
  """
  if term:
    print "Running on one term: %s" % str(term)
    search_page = urllib2.urlopen(LIST_URL.format(term=term))
    courseids = get_course_list(search_page)
    for id in courseids:
      try:
        save_html(id, term)
      except Exception:
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write('Error processing course id {0}\n'.format(id))
  else:
    print "Running on all given terms"
    for key, t in termss.iteritems():
      print t
      print "Getting master list of courses from this term..."
      search_page = urllib2.urlopen(LIST_URL.format(term=t))
      print "Converting to individual course IDs..."
      courseids = get_course_list(search_page)
      print "Working through IDs..."
      for id in courseids:
        try:
          save_html(id, t)
        except Exception:
          import traceback
          traceback.print_exc(file=sys.stderr)
          sys.stderr.write('Error processing course id {0}\n'.format(id))

# Returns a unique filename for each file
def getfilename(course, term):
  filename = str(term) + "_"
  for listing in course['listings']:
    filename = filename + str(listing)
  if course['listings'] is None:
    filename = filename + 'REL_SEM'
  return filename


# Main executable. Checks to see if commandline arg given (i.e. only want to run
# for one term, in which case use 1144 for example, not literal Fall/Spring text!)
# If no arg given, runs for all uncommented terms in termss at top of code.
if __name__ == "__main__":
  
#  if len(sys.argv) > 1:
#    print "Just one"
#    term = str(sys.argv[1])
#    scrape_all(term)
#  else:
  print "All"
  scrape_all()
