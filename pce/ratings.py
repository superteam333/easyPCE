import os
import re
import sys
sys.path.append('/srv/www/myapp/')
from myapp import settings
from django.core.management import setup_environ
setup_environ(settings)
from models import *

# some constants
NO_RATING = -100000
wri = Department.objects.get(dept="WRI")

#all_courses = Course.objects.order_by('regNum', '-year', '-semester')
#unique = []
#prev_r = -1
#for c in all_courses:
#	if c.regNum != prev_r:
#		prev_r = c.regNum
#		unique.append(c)
#print len(all_courses)
#print len(unique)

cnums = CourseNum.objects.all()
n_arr = []
r_arr = []
for cn in cnums:
	ni = 0
	instances = Course.objects.filter(coursenum=cn)
	for i in instances:
		evals = Evaluation.objects.filter(instance=i, questiontext="I think that the overall quality of the course was:")
		if len(evals) == 0:
			evals = Evaluation.objects.filter(instance=i, questiontext="Overall quality of the writing seminar")
		for e in evals:
			ni = ni + e.num_responses
	if ni != 0:
		if not cn.avg:
			print cn 
		ri = float(cn.avg)
	else:
		ri = NO_RATING
		ni = NO_RATING
	n_arr.append(ni)
	r_arr.append(ri)	

#print "calculated ni and ri"

N = 0
NR = 0
for i in range(0, len(n_arr)):
	ni = n_arr[i]
	ri = r_arr[i]
	if ni != NO_RATING:
		N = N + ni
		#R = R + ri
		NR = NR + ni*ri
#print N
#print NR

b_ratings = []
for i in range(0, len(n_arr)):
	ni = n_arr[i]
	ri = r_arr[i]
	if ni == NO_RATING:
		b_ratings.append(0)
	else:
		bi = (NR + ni*ri) / (N + ni)
		b_ratings.append(bi)

#print calculated b

cb_zipped = zip(cnums, b_ratings)
cb_zipped.sort(key=lambda tup: -tup[1])

#print len(cb_zipped)

prev_r = -1
i = 0
c_set = set()
while i < len(cb_zipped):
	cna = cb_zipped[i]
	cn = cna[0]
	#cn = cb_zipped[i][0]
	courses = cn.instance.all().order_by('-year', '-semester')
	if len(courses) > 0:
		#c = courses[0]
		new = True
		for ci in courses:
			if ci.id not in c_set:
				c_set.add(ci.id)
			else:
				new = False
				break
		if new == True:
			i = i+1
			print "%s" % cn
		else:
			cb_zipped.pop(i)
			#print "removed: %s - %s" % (cn, cb_zipped[i][1])
	else:
		cb_zipped.pop(i)
		#print "empty + removed: %s" % (cn)
	#if c.regNum == prev_r:
	#	cb_zipped.pop(i)
	#	print "removed: %s - %s" % (cn, cb_zipped[i][1])
	#else:
	#	prev_r = c.regNum
	#	i = i+1

#print len(cb_zipped)
#for c, b in cb_zipped:
#	print "%s: %s" % (c, b)
