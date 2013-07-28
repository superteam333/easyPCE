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
	return course_set.distinct().filter(id__in=ids)

def coursesByDepartment(depts, course_set):
	if course_set is None or len(course_set) == 0:
		course_set = Course.objects

	try:
		return course_set.filter(coursenum__dept__dept__in=depts)
	except Exception as inst:
		return HttpResponse("F***%s | %s" % (type(inst), inst))

	return None

def coursesByDistribution(das, course_set):
	if course_set is None or len(course_set) == 0:
		course_set = Course.objects

	try:
		return course_set.filter(da__in=das)
	except Exception as inst:
		return HttpResponse("F***%s %s" % (type(inst), inst))

	return None

def coursesByProfessor(profs, course_set):
	if course_set is None or len(course_set) == 0:
		course_set = Course.objects

	try:
		return course_set.filter(profs__in=profs)
	except Exception as inst:
		return HttpResponse("F***%s %s" % (type(inst), inst))

	return None

def coursesByDateTime(dateTime, course_set):
	if course_set is None or len(course_set) == 0:
		course_set = Course.objects

	try:
		return course_set.filter(lectureTime__icontains=dateTime)
	except Exception as inst:
		return HttpResponse("F***%s %s" % (type(inst), inst))

	return None

def coursesByAdvice(advice, course_set):
	if course_set is None or len(course_set) == 0:
		course_set = Course.objects

	try:
		result = course_set.filter(advice__text__icontains=advice[0])
		for i in range(1, len(advice)-1):
			result = result | course_set.filter(advice__text__icontains=advice[i])
		return result
	except Exception as inst:
		return HttpResponse("F***%s %s" % (type(inst), inst))
		#pass

def isAdvice(qAdvice):
	return 

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


	all_depts = Department.objects.all().order_by('dept')

	html = "<ul>"

	czipped = []
	pzipped = []
	dzipped = []

	courses = None

	qAdvice = request.GET.getlist("advice")
	qDepts = request.GET.getlist("depts")
	qProfs = request.GET.getlist("profs")
	qDist = request.GET.getlist("dist")
	qDays = request.GET.getlist("days")

	mostRecent = not (qAdvice and qAdvice[0])

	# Departments
	if qDepts and qDepts[0]:
		for i in range(len(qDepts)):
			qDepts[i] = qDepts[i][:3].upper()

		if not courses and mostRecent:
			courses = onlyMostRecent(coursesByDepartment(qDepts, courses))
		else:
			courses = coursesByDepartment(qDepts, courses)

	# Professors
	if qProfs and qProfs[0]:
		profs = []
		for i in range(len(qProfs)):
			words = qProfs[i].split()
			qs = Professor.objects.filter(lastname__icontains=words[-1])				
			for i in range(1, len(words)-1):
				qs = qs.filter(firstname__icontains=words[i])
			set = Set([])
			for p in qs:
				if p not in set:
					set.add(p)
					profs.append(p)
			qs = Professor.objects.filter(firstname__icontains=words[-1])
			for i in range(1, len(words)-1):
				qs = qs.filter(lastname__icontains=words[i])
			for p in qs:
				if p not in set:
					set.add(p)
					profs.append(p)
		if profs:
			if not courses and mostRecent:
				courses = onlyMostRecent(coursesByProfessor(profs, courses))
			else:
				courses = coursesByProfessor(profs, courses)

	# Distribution Areas
	if qDist and qDist[0]:
		das = []
		for i in range(len(qDist)):
			das.append(qDist[i].upper())

		if not courses or mostRecent:
			courses = onlyMostRecent(coursesByDistribution(das, courses))
		else:
			courses = coursesByDistribution(das, courses)

	# Days
	if qDays and qDays[0]:
		days = ""
		for d in qDays:
			days = days + " " + d

		if not courses and mostRecent:
			courses = onlyMostRecent(coursesByDateTime(days, courses))
		else:
			courses = coursesByDateTime(days, courses)
		#return HttpResponse(courses)

	# Advice
	if qAdvice and qAdvice[0]:
		courses = onlyMostRecent(coursesByAdvice(qAdvice, courses))

	# display the results
	links = []
	courses = courses.order_by('coursenum__dept__dept', 'coursenum__number', 'title')
	for c in courses:
		cnum = c.coursenum_set.all()[0]
		dept = cnum.dept.dept
		n = cnum.number        

		nums = c.coursenum_set.all().order_by('dept__dept')
		numString = "%s" % nums[0]
		for a in range(1, len(nums)):
			numString = "%s / %s" % (numString, nums[a])		

		a = '<a href="/courses/%s%s">%s: %s</a>' % (dept, n, numString, c.title)
		links.append(a)

	czipped = zip(courses, links)

	if (czipped):
		t = get_template('search_results.html')
		html = t.render(Context({'courses':czipped, 'profs':pzipped, 'depts':dzipped, 'query':"query", 'user':user, 'alldepts':all_depts}))
		return HttpResponse(html)	

	list = qDepts
	
	t = get_template('search_empty.html')
	return HttpResponse(t.render(Context({'user':user, 'q':"query", 'alldepts':all_depts})))