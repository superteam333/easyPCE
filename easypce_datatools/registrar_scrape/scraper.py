#!/usr/bin/env python
"""
Modified by John Whelchel for COS333 
Spring 2013


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

termss = dict()
termss['Fall_2006-2007']=1072
termss['Fall_2007-2008']=1082
termss['Fall_2008-2009']=1092
termss['Fall_2009-2010']=1102
termss['Fall_2010-2011']=1112
termss['Fall_2011-2012']=1122
termss['Fall_2012-2013']=1132
termss['Fall_2013-2014']=1142
termss['Fall_2014-2015']=1152
termss['Spring_2006-2007']=1074
termss['Spring_2007-2008']=1084
termss['Spring_2008-2009']=1094
termss['Spring_2009-2010']=1104
termss['Spring_2010-2011']=1114
termss['Spring_2011-2012']=1124
termss['Spring_2012-2013']=1134
termss['Spring_2013-2014']=1144


TERM_CODE = 'Fall_2014-2015'
URL_PREFIX = "http://registrar.princeton.edu/course-offerings/"
LIST_URL = URL_PREFIX + "search_results.xml?term={term}"
COURSE_URL = URL_PREFIX + "course_details.xml?courseid={courseid}&term={term}"

COURSE_URL_REGEX = re.compile(r'courseid=(?P<id>\d+)')
PROF_URL_REGEX = re.compile(r'dirinfo\.xml\?uid=(?P<id>\d+)')
LISTING_REGEX = re.compile(r'(?P<dept>[A-Z]{3})\s+(?P<num>\w{2,4})')

def get_course_list(search_page):
  "Grep through the document for a list of course ids."
  soup = BeautifulSoup(search_page)
  links = soup('a', href=COURSE_URL_REGEX)
  courseids = [COURSE_URL_REGEX.search(a['href']).group('id') for a in links]
  return courseids

def clean(str):
  "Return a string with leading and trailing whitespace gone and all other whitespace condensed to a single space."
  return re.sub('\s+', ' ', str.strip())

def get_course_details(soup):
  "Returns a dict of {courseid, area, title, descrip, prereqs}."
  match = re.match(r'\(([A-Z]+)\)', clean(soup('strong')[1].findNext(text=True)))
  if match == None:
     print match
  print "Look here!" +  str(clean(soup('strong')[1].findNext(text=True)))
  pretitle = soup.find(text="Prerequisites and Restrictions:")
  descrdiv = soup.find('div', id='descr')
  #darea = match.group(1)
  #print darea
  return {
    'courseid': COURSE_URL_REGEX.search(soup.find('a', href=COURSE_URL_REGEX)['href']).group('id'),
    'area': match.group(1) if match != None else '',
    'title': clean(soup('h2')[1].string),
    'descrip': clean(descrdiv.contents[0] if descrdiv else ''),
    'prereqs': clean(pretitle.parent.findNextSibling(text=True)) if pretitle != None else ''
  }

def get_course_listings(soup):
  "Return a list of {dept, number} dicts under which the course is listed."
  listings = soup('strong')[1].string
  return [{'dept': match.group('dept'), 'number': match.group('num')} for match in LISTING_REGEX.finditer(listings)]

def get_course_profs(soup):
  "Return a list of {uid, name} dicts for the professors teaching this course."
  prof_links = soup('a', href=PROF_URL_REGEX)
  return [{'uid': PROF_URL_REGEX.search(link['href']).group('id'), 'name': clean(link.string)} for link in prof_links]

def get_single_class(row):
  "Helper function to turn table rows into class tuples."
  cells = row('td')
  time = cells[2].string.split("-")
  bldg_link = cells[4].strong.a
  return {
    'classnum': cells[0].strong.string,
    'days': re.sub(r'\s+', '', cells[3].strong.string),
    'starttime': time[0].strip(),
    'endtime': time[1].strip(),
    'bldg': bldg_link.string.strip(),
    'roomnum': bldg_link.nextSibling.string.replace('&nbsp;', ' ').strip()
  }

def get_course_classes(soup):
  "Return a list of {classnum, days, starttime, endtime, bldg, roomnum} dicts for classes in this course."
  class_rows = soup('tr')[1:] # the first row is actually just column headings
  # This next bit tends to cause problems because the registrar includes precepts and canceled
  # classes. Having text in both 1st and 4th columns (class number and day of the week)
  # currently indicates a valid class.
  return [get_single_class(row) for row in class_rows if row('td')[0].strong and row('td')[3].strong.string]

def scrape_page(page):
  "Returns a dict containing as much course info as possible from the HTML contained in page."
  soup = BeautifulSoup(page).find('div', id='contentcontainer')
  course = get_course_details(soup)
  course['listings'] = get_course_listings(soup)
  course['profs'] = get_course_profs(soup)
  course['classes'] = get_course_classes(soup)
  return course

def scrape_id(id):
  #print id
  page = urllib2.urlopen(COURSE_URL.format(term=termss[TERM_CODE], courseid=id))
  return scrape_page(page)

def scrape_all():
  """
  Return an iterator over all courses listed on the registrar's site.
  
  Which courses are retrieved are governed by the globals at the top of this module,
  most importantly LIST_URL and TERM_CODE.

  To be robust in case the registrar breaks a small subset of courses, we trap
  all exceptions and log them to stdout so that the rest of the program can continue.
  """
  print TERM_CODE
  print termss[TERM_CODE]
  print LIST_URL.format(term=termss[TERM_CODE])
  search_page = urllib2.urlopen(LIST_URL.format(term=termss[TERM_CODE]))
  courseids = get_course_list(search_page)
  for id in courseids:
    try:
      yield scrape_id(id)
    except Exception:
      import traceback
      traceback.print_exc(file=sys.stderr)
      sys.stderr.write('Error processing course id {0}\n'.format(id))

def getfilename(course):
  filename = TERM_CODE + "_"
  for listing in course['listings']:
    filename = filename + str(listing)
  if course['listings'] is None:
    filename = filename + 'REL_SEM'
  return filename

if __name__ == "__main__":
  
  if len(sys.argv) > 1:
    TERM_CODE = str(sys.argv[1])
  #first = True
  for course in scrape_all():
    if(os.path.exists('/home/ubuntu/registrar_scrape/FULL_DATA/' + getfilename(course))):
      continue
    f = open(getfilename(course), 'w')
    print course['listings']
    #if first:
      #first = False
      #print '['
    #else:
      #print ','
    f.write("[")
    json.dump(course, f)
    f.write("]")
    #print ']'
