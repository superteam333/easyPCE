import os
import re
import sys
sys.path.append('/srv/www/myapp/')
from myapp import settings
from django.core.management import setup_environ
setup_environ(settings)
from models import *
import HTMLParser

hp = HTMLParser.HTMLParser() #needed to fix HTML entities in database from parsing

# some constants
NO_RATING = -100000
wri = Department.objects.get(dept="WRI")

all_courses = Course.objects.order_by('regNum', '-year', '-semester')
unique_courses = []
prev_r = -1
for c in all_courses:
	if c.regNum != prev_r:
		prev_r = c.regNum
		unique_courses.append(c)

print "Courses"
course_strings = []
for c in unique_courses:
	cnums = c.coursenum_set.all().order_by('dept__dept')
	if len(cnums) > 0:
		s = cnums[0]
		for i in range(1, len(cnums)):
			s = "%s / %s" % (s, cnums[i])
		s = "%s: %s" % (s, c.title)
		course_strings.append(s)
		try:
			pattern = re.compile(r'<.*?>')
			print pattern.sub('', hp.unescape(s))
		except:
			pass

print "*Departments"
all_depts = Department.objects.order_by('dept')
for d in all_depts:
	print "%s: %s" % (d.dept, d.name)

print "*Professors"
all_profs = Professor.objects.order_by('firstname', 'lastname')
for p in all_profs:
	try:
		print "%s %s" % (p.firstname, p.lastname)
	except:
		pass

#all_courses = Course.objects.order_by('title')
#course_set = set()
#unique_courses = []
#for c in all_courses:
#	cnums = c.coursenum_set.all()
#	for n in cnums:
#		s = n + 
#	t = c.title
#	if t != prev_t:
#		prev_t = t
#		unique_titles.append(t)

#print "Course Titles:"
#for t in unique_titles:
#	print t
