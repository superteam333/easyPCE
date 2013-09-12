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
import time

class SortType:
	RANK = 0
	TITLE = 1
	ADVICE = 2

def onlyMostRecent(course_set):
	regNums = [c.regNum for c in course_set]
	ids = []
	course_set = Course.objects.filter(regNum__in=regNums).order_by('regNum', '-year', '-semester')
	prevRegNum = None
	for c in course_set:
		if (c.regNum != prevRegNum):
			ids.append(c.id)
			prevRegNum = c.regNum

	return course_set.distinct().filter(id__in=ids)

def onlyThisSemester(course_set):
	# if not course_set:
	# 	course_set = Course.objects

	try:
		return course_set.filter(year='2013-2014', semester__iexact='fall')
	except Exception as inst:
		return HttpResponse("F***%s | %s" % (type(inst), inst))

	return None

def coursesByDepartment(depts, course_set):
	if not course_set:
		course_set = Course.objects

	try:
		return course_set.filter(coursenum__dept__dept__in=depts)
	except Exception as inst:
		return HttpResponse("F***%s | %s" % (type(inst), inst))

	return None

def coursesByDistribution(das, course_set):
	if not course_set:
		course_set = Course.objects

	try:
		return course_set.filter(da__in=das)
	except Exception as inst:
		return HttpResponse("F***%s %s" % (type(inst), inst))

	return None

def coursesByProfessor(profs, course_set):
	if not course_set:
		course_set = Course.objects

	try:
		return course_set.filter(profs__in=profs)
	except Exception as inst:
		return HttpResponse("F***%s %s" % (type(inst), inst))

	return None

def coursesByDay(days, course_set):
	if not course_set:
		course_set = Course.objects

	try:
		return course_set.filter(lectureTime__icontains=days)
	except Exception as inst:
		return HttpResponse("F***%s %s" % (type(inst), inst))

	return None

def coursesByTime(times, course_set):
	if not course_set:
		course_set = Course.objects

	try:
		return course_set.filter(lectureTime__regex=times)
	except Exception as inst:
		return HttpResponse("F***%s %s" % (type(inst), inst))

	return None

def coursesByAdvice(advice, course_set):
	if not course_set:
		course_set = Course.objects

	try:
		result = course_set.filter(advice__text__icontains=advice[0])
		for a in advice[1:]:
			result = result | course_set.filter(advice__text__icontains=a)
		return result
	except Exception as inst:
		return HttpResponse("F***%s %s" % (type(inst), inst))
		#pass

def coursesByPdf(pdf, course_set):
	if not course_set:
		course_set = Course.objects

	try:
		if pdf == '0':
			return course_set.filter(nopdf=1)
		elif pdf == '1':
			return course_set.filter(nopdf=0)
		elif pdf == '2':
			return course_set.filter(pdf=1)
		else:
			return course_set;
	except Exception as inst:
		return HttpResponse("F***%s %s" % (type(inst), inst))

	return None

def search(request):
	now = time.time()
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

	courses = Course.objects.all()

	query = {}
	query['adv'] = []

	qAdvice = request.GET.getlist("advice[]")
	qDepts = request.GET.getlist("depts[]")
	qProfs = request.GET.getlist("profs[]")
	qDist = request.GET.getlist("dist[]")
	qDays = request.GET.getlist("days[]")
	qTimes = request.GET.getlist("times[]")
	qPdf = request.GET.getlist("pdf[]")
	qSem = request.GET.get('sem')

	isAdvice = qAdvice and qAdvice[0]
	usePrev = qSem == 'a'

	if not isAdvice:
		if usePrev:
			course = onlyMostRecent(courses)
		else:
			courses = onlyThisSemester(courses)


	# Departments
	if qDepts and qDepts[0]:
		for i in range(len(qDepts)):
			qDepts[i] = qDepts[i][:3].upper()

		courses = coursesByDepartment(qDepts, courses)

		query['adv'].append({'title':'Department', 'items':qDepts})

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
			courses = coursesByProfessor(profs, courses)

		query['adv'].append({'title':'Professor', 'items':[p.split()[-1] for p in qProfs]})

	# Distribution Areas
	if qDist and qDist[0]:
		das = []
		for i in range(len(qDist)):
			das.append(qDist[i].upper())

		courses = coursesByDistribution(das, courses)

		query['adv'].append({'title':'Distribution', 'items':das})

	# Days
	if qDays and qDays[0]:
		days = qDays[0]
		for d in qDays[1:]:
			days = days + " " + d

		courses = coursesByDay(days, courses)

		query['adv'].append({'title':'Day', 'items':[days]})

	# Time
	if qTimes and qTimes[0]:
		res = [';'+x+':[0-9]{2} '+('am' if int(x)>8 and int(x)<12 else 'pm')+','  for x in qTimes]
		times = '(' + res[0] + ''.join('|'+x for x in res[1:]) + ')'

		courses = coursesByTime(times, courses)

		query['adv'].append({'title':'Time', 'items':[x+':00 '+('am' if int(x)>8 and int(x)<12 else 'pm') for x in qTimes]})

	# PDF
	if qPdf and qPdf[0]:
		p = qPdf[0]
		courses = coursesByPdf(p, courses)

		t = 'can pdf'
		if p == '0':
			t = 'no pdf'
		if p == '2':
			t = 'only pdf'

		query['adv'].append({'title':'PDF Option', 'items':[t]})

	if usePrev:
		query['adv'].append({'title':'Semester', 'items':['all']})
	else:
		query['adv'].append({'title':'Semester', 'items':['current']})

	# Advice
	adviceInstances = {}
	if isAdvice:
		cba = coursesByAdvice(qAdvice, courses)
		courses = onlyMostRecent(cba)
		if not usePrev:
			courses = onlyThisSemester(courses)
			

		cba = cba.order_by('regNum')
		prev_r = -1
		for x in cba:
			r = x.regNum
			if r == prev_r:
				adviceInstances[r].append(x.id)
			else:
				adviceInstances[r] = [x.id]
				prev_r = r

		query['adv'].append({'title':'Advice', 'items':qAdvice})

	done = time.time()

	# display the results
	#courses = onlyThisSemester(courses)
	if not courses:
		# return HttpResponse("") #should display an error page
		t = get_template('search_results.html')
		html = t.render(Context({'courses':None, 'profs':None, 'depts':None, 'query':query, 'user':user, 'alldepts':all_depts}))
		return HttpResponse(html)

	sort = request.GET.get('sort')
	if not sort:
		if isAdvice:
			sort = SortType.ADVICE
		else:
			sort = SortType.RANK
	else:
		sort = int(sort)

	
	if sort == SortType.TITLE:
		courses = courses.order_by('coursenum__dept__dept', 'coursenum__number', 'title').distinct()
	elif sort == SortType.RANK:
		courses = courses.order_by('-coursenum__bayes').distinct()
	elif sort == SortType.ADVICE and isAdvice:
		#return HttpResponse(str(courses))
		counts = [Advice.objects.filter(instance__id__in=adviceInstances[x.regNum], text__icontains=qAdvice[0]).count() for x in courses]
		#return HttpResponse(counts[0])
		courses = zip(*sorted(zip(courses, counts), key=lambda t: -t[1]))[0]


	start = 0
	pageSize = 25 if request.is_ajax() else 50
	pn = request.GET.get('pg')
	if pn:
		start = int(pn) * pageSize
	end = min(start + pageSize, len(courses))

	if start > len(courses):
		return HttpResponse("")

	links = []
	rating = []
	dayTimes = []
	profs = []
	advice = []

	for c in courses[start:end]:
		if not c.coursenum_set.exists():
			continue

		cnum = c.coursenum_set.all()[0]
		dept = cnum.dept.dept
		n = cnum.number        

		nums = c.coursenum_set.all().order_by('dept__dept')
		numString = "%s" % nums[0]
		for a in range(1, len(nums)):
			numString = "%s / %s" % (numString, nums[a])		

		a = '<a class="courseTitle" href="/courses/%s%s">%s: %s</a>' % (dept, n, numString, c.title)
		links.append(a)

		profs.append(c.profs.all())

		# 0=empty, 1=half, 2=full
		r = []
		avg = 0
		try:
			avg = float(cnum.avg) 
		except Exception as inst:
			pass
		dec = avg - int(avg)
		full = int(avg)
		if dec >= .75:
			full = full + 1
		for x in range(full):
			r.append(2)

		if dec > .25 and dec < .75:
			r.append(1)

		for x in range(len(r),5):
			r.append(0)
		
		r.append(avg)

		rating.append(r)

		lecTime = c.lectureTime
		if lecTime:
			dayTime = lecTime.split(';')
			d = [x.replace(' ','') for x in dayTime[::2]]
			t = [x.replace(' ','').split(',') for x in dayTime[1::2]]
			dayTimes.append(zip(d,t))

		if adviceInstances:
			adText = qAdvice[0]
			if c.regNum in adviceInstances:
				adv = Advice.objects.filter(instance__id__in=adviceInstances[c.regNum], text__icontains=qAdvice[0])
				for a in adv:
					f = a.text.lower().find(adText.lower())
					a.text = '%s<span class="highlight">%s</span>%s' % (a.text[0:f], a.text[f:f+len(adText)], a.text[f+len(adText):])
				advice.append(adv)

	# v = int([])

	if isAdvice:
		czipped = zip(courses[start:end], links, rating, profs, dayTimes, advice)
	else:
		czipped = zip(courses[start:end], links, rating, profs, dayTimes)
	if request.is_ajax():
		if czipped:
			t = get_template('searchResultsCourseList.html')
			html = t.render(Context({'courses':czipped}))
			return HttpResponse(html)
		else:
			return HttpResponse("")

	bef = time.time()
	# return HttpResponse(str(bef-now))

	if (czipped):
		t = get_template('search_results.html')
		html = t.render(Context({'courses':czipped, 'profs':pzipped, 'depts':dzipped, 'query':query, 'user':user, 'alldepts':all_depts}))
		return HttpResponse(html)	

	list = qDepts
	
	t = get_template('search_empty.html')
	return HttpResponse(t.render(Context({'user':user, 'q':"query", 'alldepts':all_depts})))