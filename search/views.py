from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
import os
from django.template import Context, loader, RequestContext
from django.template.loader import get_template
import re
from pce.models import *
from sets import Set
from django.views.decorators.csrf import csrf_exempt
from django.http import QueryDict
import simplejson
import _ssl;_ssl.PROTOCOL_SSLv23 = _ssl.PROTOCOL_SSLv3
import urllib, re

def onlyMostRecent(course_set):
	ids = []
	course_set = course_set.all().order_by('regNum', '-year', '-semester')
	prevRegNum = None
	for c in course_set:
		if (c.regNum != prevRegNum):
			ids.append(c.id)
			prevRegNum = c.regNum
	return course_set.filter(id__in=ids)

def coursesByDepartment(dept, course_set):
	if course_set is None or len(course_set) == 0:
		course_set = Course.objects

	try:
		return course_set.filter(coursenum__dept=dept)
	except Exception as inst:
		return HttpResponse("F***%s %s" % (type(inst), inst))

	return None

def coursesByDistribution(da, course_set):
	if course_set is None or len(course_set) == 0:
		course_set = Course.objects

	try:
		return course_set.filter(da__iexact=da)
	except Exception as inst:
		return HttpResponse("F***%s %s" % (type(inst), inst))

	return None

def coursesByProfessor(prof, course_set):
	if course_set is None or len(course_set) == 0:
		course_set = Course.objects

	try:
		return course_set.filter(profs=prof)
	except Exception as inst:
		return HttpResponse("F***%s %s" % (type(inst), inst))

	return None

def coursesByTime(time, course_set):
	if course_set is None or len(course_set) == 0:
		course_set = Course.objects

	try:
		return course_set.filter(lectureTime__icontains=time)
	except Exception as inst:
		return HttpResponse("F***%s %s" % (type(inst), inst))

	return None

def coursesByAdvice(advice, course_set):
	if course_set is None or len(course_set) == 0:
		course_set = Course.objects

	try:
		n = 0
		tupleList = []
		instances = course_set.all().order_by('regNum', '-year', '-semester')
		if instances is not None and len(instances) > 0:
			i = 0
			while i < len(instances):
				prevRegNum = instances[i].regNum
				course = instances[i]

				# get advice for all of the instances of a course
				course_instances = []
				while (i < len(instances) and instances[i].regNum == prevRegNum ):
					course_instances.append(instances[i])
					i = i + 1
				course_advice = Advice.objects.filter(instance__in=course_instances, text__icontains=advice).exclude(text__icontains=("not")) 

				if len(course_advice) != 0:
					tupleList.append((course, course_advice))
				i = i+1

			tupleList.sort(key = lambda t: -len(t[1]))
			return tupleList
		return None
	except Exception as inst:
		return HttpResponse("F***%s %s" % (type(inst), inst))
		#pass

def search(request):
	if not settings.DEBUG:
		try:
			n = request.session['netid']
			if request.session['netid'] is None:
				return check_login(request, '/')
		except:
			return check_login(request, '/')
		netid = request.session['netid']
	else:
		netid = 'dev'

	try:
	    user= User.objects.get(netid=netid)
	except:
		user=User(netid=netid)
		user.save()

	html = "<ul>"
	#list = onlyMostRecent(coursesByDepartment(Department.objects.filter(dept__iexact='COS'), None))
	#list = onlyMostRecent(coursesByDistribution("la", None))
	#list = onlyMostRecent(Course.objects)
	# list = coursesByDepartment(Department.objects.filter(dept__iexact='COS'), None)
	# list = coursesByDistribution("qr", list)
	# list = coursesByTime("T Th", list)
	# list = onlyMostRecent(list)
	#list = coursesByProfessor(Professor.objects.filter(id=313), None)

	for blah in list:
		html = html + "<li>" + blah.title + "</li>"
	return HttpResponse(html)

	if 'q' in request.GET and request.GET['q']:
		q = request.GET['q']
		words = q.split()
		errors = "Errors:\n"
		
		czipped = []
		pzipped = []
		dzipped = []
		
		# Check for "text search" in something
		if re.search('^\".*\"', q) is not None:
			text = re.search('^\".*\"', q).group(0)
			text = text[1:-1]
			after = q[len(text)+2:]
			inIndex = after.find('in ')
			if inIndex != -1:
				after = after[inIndex+3:]
			if re.search("^[a-zA-Z]{2,3}", after) is not None:
				# text search in a distribution area
				try:
					courseList = []
					adviceList = []
					instances = Course.objects.filter(da=after).order_by('regNum', '-year', '-semester')
					sorted = coursesByAdvice(text, instances)
					#return(sorted)
					
					if len(sorted):
						links = []
						for c, al in sorted:
							ccnums = c.coursenum_set.all().order_by("dept__dept")
							numString = '<a href="/courses/%s%s">%s' % (ccnums[0].dept.dept, ccnums[0].number, ccnums[0])
							for li in range(1, len(ccnums)):
								numString = "%s / %s" % (numString, ccnums[li])
							numString = "%s: %s</a>" % (numString, c.title)
							links.append(numString)
							for a in al:
								f = a.text.lower().find(text.lower())
								a.text = '%s<span id="highlight">%s</span>%s' % (a.text[0:f], a.text[f:f+len(text)], a.text[f+len(text):])
						courseList, adviceList = zip(*sorted)
						res = zip(links,adviceList,courseList)
						t = get_template('textsearch.html')
						ds = Department.objects.all().order_by('dept')
						html = t.render(Context({'results':res,'query':q, 'user':user, 'alldepts':ds}))
						return HttpResponse(html)
				except Exception as inst:
					return HttpResponse("***%s %s" % (type(inst), inst))
					#pass
	return HttpResponse("hi")