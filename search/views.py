from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
import os
from django.template import Context, loader, RequestContext
from django.template.loader import get_template
import re
from pce.models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import QueryDict
import simplejson
import _ssl;_ssl.PROTOCOL_SSLv23 = _ssl.PROTOCOL_SSLv3
import urllib, re
import time
import itertools

class SortType:
	RANK = 0
	TITLE = 1
	ADVICE = 2

def onlyMostRecent(course_set):
	# get all courses instances that corresponded to the given regNums
	regNums = [c.regNum for c in course_set]
	course_set = Course.objects.filter(regNum__in=regNums).order_by('regNum', '-year', '-semester')
	
	# get the id of only the most recent of each regNum in the set
	ids = []
	prevRegNum = None
	for c in course_set:
		if (c.regNum != prevRegNum):
			ids.append(c.id)
			prevRegNum = c.regNum

	# return only the most recent courses
	return course_set.distinct().filter(id__in=ids)

def onlyThisSemester(course_set):
	try:
		return course_set.filter(year='2013-2014', semester__iexact='fall')
	except Exception as inst:
		return HttpResponse("%s | %s" % (type(inst), inst))

	return None

def coursesByDepartment(depts, course_set):
	try:
		return course_set.filter(coursenum__dept__dept__in=depts)
	except Exception as inst:
		return HttpResponse("%s | %s" % (type(inst), inst))

	return None

def coursesByDistribution(das, course_set):
	try:
		return course_set.filter(da__in=das)
	except Exception as inst:
		return HttpResponse("%s %s" % (type(inst), inst))

	return None

def coursesByProfessor(profs, course_set):
	try:
		return course_set.filter(profs__in=profs)
	except Exception as inst:
		return HttpResponse("%s %s" % (type(inst), inst))

	return None

def coursesByTime(times, course_set):
	try:
		return course_set.filter(lectureTime__regex=times)
	except Exception as inst:
		return HttpResponse("%s %s" % (type(inst), inst))

	return None

def coursesByAdvice(advice, course_set):
	try:
		result = course_set.filter(advice__text__icontains=advice[0])
		for a in advice[1:]:
			result = result | course_set.filter(advice__text__icontains=a)
		return result
	except Exception as inst:
		return HttpResponse("%s %s" % (type(inst), inst))

	return None

def coursesByPdf(pdf, course_set):
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
		return HttpResponse("%s %s" % (type(inst), inst))

	return None

def isAdvanced(request):
	if request.GET.getlist("advice[]"):
		return True
	if request.GET.getlist("depts[]"):
		return True
	if request.GET.getlist("profs[]"):
		return True
	if request.GET.getlist("dist[]"):
		return True
	if request.GET.getlist("days[]"):
		return True
	if request.GET.getlist("times[]"):
		return True
	if request.GET.getlist("pdf[]"):
		return True
	if request.GET.getlist("sem"):
		return True

	if not request.GET.get("q"):
		return True

	return False
	

def advancedSearch(request, user):
	all_depts = Department.objects.all().order_by('dept')
	courses = Course.objects.all()

	czipped = []

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
			pSet = set()
			for p in qs:
				if p not in pSet:
					pSet.add(p)
					profs.append(p)
			qs = Professor.objects.filter(firstname__icontains=words[-1])
			for i in range(1, len(words)-1):
				qs = qs.filter(lastname__icontains=words[i])
			for p in qs:
				if p not in pSet:
					pSet.add(p)
					profs.append(p)
		if profs:
			courses = coursesByProfessor(profs, courses)
		else:
			courses = Course.objects.none()

		query['adv'].append({'title':'Professor', 'items':[p.split()[-1] for p in qProfs]})

	# Distribution Areas
	if qDist and qDist[0]:
		das = []
		for i in range(len(qDist)):
			das.append(qDist[i].upper())

		courses = coursesByDistribution(das, courses)

		query['adv'].append({'title':'Distribution', 'items':das})

	# Day and Time search
	dayCombs = []
	timeREs = []
	if qDays and qDays[0]:
		dayCombs = []
		for i in range(len(qDays)):
			for c in itertools.combinations(qDays, i+1):
				dayCombs.append(" ".join(d for d in c))

		dayString = " ".join(d for d in qDays)
		query['adv'].append({'title':'Day', 'items':[dayString]})

	if qTimes and qTimes[0]:
		timeREs = [';'+x+':[0-9]{2} '+('am' if int(x)>8 and int(x)<12 else 'pm')+','  for x in qTimes]
		query['adv'].append({'title':'Time', 'items':[x+':00 '+('am' if int(x)>8 and int(x)<12 else 'pm') for x in qTimes]})

	if dayCombs and timeREs:
		dayTimes = []
		for d in dayCombs:
			dayTimes.extend([d + " " + r for r in res])
		times = '(' +'|'.join(x for x in dayTimes) + ')' 
		courses = coursesByTime(times, courses)
	elif dayCombs:
		times = '(' + '|'.join(x for x in dayCombs) + ')'
		courses = coursesByTime(times, courses) 
	elif timeREs:
		times = '(' +'|'.join(x for x in timeREs) + ')' 
		courses = coursesByTime(times, courses)

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
	if not courses:
		t = get_template('search_results.html')
		html = t.render(Context({'query':query, 'user':user, 'alldepts':all_depts}))
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
		counts = [Advice.objects.filter(instance__id__in=adviceInstances[x.regNum], text__icontains=qAdvice[0]).count() for x in courses]
		courses = zip(*sorted(zip(courses, counts), key=lambda t: -t[1]))[0]


	start = 0
	pageSize = 25 if request.is_ajax() else 50
	pn = request.GET.get('pg')
	if pn:
		start = int(pn) * pageSize
	end = min(start + pageSize, len(courses))

	if start > len(courses):
		return HttpResponse("")

	# prepare info for displaying results
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
			if c.regNum in adviceInstances:
				adv = Advice.objects.filter(instance__id__in=adviceInstances[c.regNum], text__icontains=qAdvice[0])
				for qAdv in qAdvice[1:]:
					adv = adv | Advice.objects.filter(instance__id__in=adviceInstances[c.regNum], text__icontains=qAdv)
				for a in adv:
					for adText in qAdvice:
						f = a.text.lower().find(adText.lower())
						if f == -1:
							continue
						a.text = '%s<span class="highlight">%s</span>%s' % (a.text[0:f], a.text[f:f+len(adText)], a.text[f+len(adText):])
				advice.append(adv)

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
	
	t = get_template('search_results.html')
	html = t.render(Context({'courses':czipped,'query':query, 'user':user, 'alldepts':all_depts}))
	return HttpResponse(html)	

def search(request):
	now = time.time()
	if not settings.DEBUG:
		try:
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


	if request.GET.get('q'):
		return basicSearch(request, user)
	elif isAdvanced(request):
		return advancedSearch(request, user)
	
	t = get_template('search_results.html')
	html = t.render(Context({'query':'', 'user':user, 'alldepts':all_depts}))
	return HttpResponse(html)	

# this is the old search function
# could probably be cleaned up
def basicSearch(request, user):
	query = {}
	query['simple'] = ''
	if 'q' in request.GET and request.GET['q']:
		q = request.GET['q']
		query['simple'] = q
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
					if instances is not None and len(instances) > 0:
						i = 0
						while i < len(instances):
							a = []
							prev_r = instances[i].regNum
							courseList.append(instances[i])
							while (i < len(instances) and instances[i].regNum == prev_r ):
								advice = Advice.objects.filter(instance=instances[i], text__icontains=text).exclude(text__icontains=("not")) # can sort on length filed here, saves srting ~10 lines later???
								if advice is not None:
									for ad in advice:
										a.append(ad)
								i = i+1	
							if len(a) != 0:
								adviceList.append(a)
							else:
								courseList.pop()
							i = i+1
						sorted = zip(courseList, adviceList)
						sorted.sort(key = lambda t: -len(t[1]))
						
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
						html = t.render(Context({'results':res,'query':query, 'user':user, 'alldepts':ds}))
						return HttpResponse(html)
				except Exception as inst:
					#return HttpResponse("***%s %s" % (type(inst), inst))
					pass
				
				# text search in a department
				try:
					d = Department.objects.get(dept=after)
					cnums = CourseNum.objects.filter(dept=d)
					courseList = []
					adviceList = []
					if cnums is not None:
						for n in cnums:
							instances = Course.objects.filter(coursenum__id=n.id).order_by('-year', '-semester')
							if instances is not None:
								a = []
								for i in range (0, len(instances)):
									if i == 0:
										courseList.append(instances[i]) # change from i to zero (John 5/7/13 3 AM)?
									advice = Advice.objects.filter(instance=instances[i], text__icontains=text).exclude(text__icontains=("not")) # can sort on length filed here, saves srting ~10 lines later???
									if advice is not None:
										for ad in advice:
											a.append(ad)
								if len(a) != 0:
									adviceList.append(a)
								else:
									courseList.pop()
						sorted = zip(courseList, adviceList)
						sorted.sort(key = lambda t: -len(t[1]))
						
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
						html = t.render(Context({'results':res,'query':query, 'user':user, 'alldepts':Department.objects.all().order_by('dept')}))
						return HttpResponse(html)
				except Exception as inst:
					#return HttpResponse("%s %s" % (type(inst), inst))
					pass
						
		# Check for only department abbreviation
		if len(words) == 1 and re.search("^[a-zA-Z]{3}$", words[0]) is not None:
			try:
				d = Department.objects.get(dept=words[0])
				return HttpResponseRedirect("/depts/%s" % d.dept)
			except Exception as inst:
				errors = errors + "\nDepartment exception: %s %s" % (type(inst), inst)
		
		# Check for DEP123				
		if (len(words) == 1 and re.search("^[a-zA-Z]{3}[0-9]+.*$", words[0]) is not None):
			dept = re.search("^[a-zA-Z]{3}", words[0]).group(0)
			num = re.search("[0-9]+.*$", words[0]).group(0)
			try:
				courses = Course.objects.filter(
					coursenum__dept=Department.objects.get(dept=dept),
					coursenum__number=num)
				if courses.count() != 0:
					course = courses[0]
					return HttpResponseRedirect("/courses/%s%s" % (dept,num))
			except Exception as inst:
				errors = errors + "\nABC123 error: %s %s" % (type(inst), inst)
				
		# Check for DEP 123		
		if (len(words) == 2 and re.search("^[a-zA-Z]{3}$", words[0]) is not None
			and re.search("[0-9]+.*", words[1]) is not None):
			try:
				courses = Course.objects.filter(
					coursenum__dept=Department.objects.get(dept=words[0]),
					coursenum__number=words[1])
				if courses.count() != 0:
					course = courses[0]
					return HttpResponseRedirect("/courses/%s%s" % (words[0], words[1]))
			except Exception as inst:
				#errors = errors + "\Course not found: %s %s" % (words[0], words[1])
				errors = errors + "\nABC 123 error: %s %s" % (type(inst), inst)
		
		# Check for professor netid
		#if (len(words) == 1):
		#	try:
		#		p = Professor.objects.get(netid=words[0])
		#		return HttpResponseRedirect("/profs/%s" % p.netid)
		#	except Exception as inst:
		#		errors = errors + "\nProf netid error: %s %s" % (type(inst), inst)
		
		# Check for Department name
		try:
			d = Department.objects.get(name=q)
			return HttpResponseRedirect("/depts/%s" % d.dept)
		except Exception as inst:
			errors = errors + "\nDept name error: %s %s" % (type(inst), inst)
		
		# Check for an exact course title
		try:
			courses = Course.objects.filter(title=q)
			if len(courses) > 0:
				c = courses[0]
				num = c.coursenum_set.all()[0]
				return HttpResponseRedirect("/courses/%s%s" % (num.dept.dept, num.number)) 
		except:
			pass
		
		# Check for course name
		# in order to make this better, need to enable fulltext search by changing database engine to MYISAM
		try:
			courses = Course.objects.filter(title__icontains=words[0])
			for i in range(1, len(words)):
				courses = courses.filter(title__icontains=words[i])
			
			if len(courses) > 0:
				cSet = set()
				unique = []
				numStrings = []
				results = ""
				for c in courses:
					nums = c.coursenum_set.all().order_by('dept__dept')
					numString = "%s" % nums[0]
					for a in range(1, len(nums)):
						numString = "%s / %s" % (numString, nums[a])
					if numString not in cSet:
						cSet.add(numString)
						unique.append(c)					
						numStrings.append(numString)
						
				# result entry may not display latest info. should fix eventually.
				links = []
				for i in range(0, len(unique)):
					c = unique[i]
					cnum = c.coursenum_set.all()[0]
					dept = cnum.dept.dept
					n = cnum.number         
					a = '<a href="/courses/%s%s">%s: %s</a>' % (dept, n, numStrings[i], c.title)
					links.append(a)
				results = results + "</ul>"
				czipped = zip(unique, links)
		except Exception as inst:
			errors = errors + "\nCourse title error: %s %s" % (type(inst), inst)
		
		# Exact Professor
		try:
			first = words[0]
			for i in range(1, len(words)-1):
				first = first + " " + words[i]
			profs = Professor.objects.filter(firstname=first, lastname=words[-1])
			if profs.count() > 0:
				return HttpResponseRedirect("/profs/%s" % profs[0].netid)
			else:
				errors = errors + "\nNo match for first: %s, last: %s" % (first, words[-1])
		except Exception as inst:
			errors = errors + "\nProf first last error: %s %s" % (type(inst), inst)
			
		# Professor options
		try:
			qs = Professor.objects.filter(lastname__icontains=words[-1])
			profs = []					
			for i in range(1, len(words)-1):
				qs = qs.filter(firstname__icontains=words[i])
			qSet = set()
			for p in qs:
				if p not in qSet:
					qSet.add(p)
					profs.append(p)
			qs = Professor.objects.filter(firstname__icontains=words[-1])
			for i in range(1, len(words)-1):
				qs = qs.filter(lastname__icontains=words[i])
			for p in qs:
				if p not in qSet:
					qSet.add(p)
					profs.append(p)
			print len(profs)
			if len(profs) > 0:
				pl = []
				for p in profs:
					a = '<a href="/profs/%s">%s %s</a>' % (p.netid, p.firstname, p.lastname)
					pl.append(a)
				pzipped = zip(profs, pl)
			else:
				errors = errors + "\nNo match for first: %s, last: %s" % (first, words[-1])
		except Exception as inst:
			errors = errors + "\nProf first last error: %s %s" % (type(inst), inst)
		
		# Department options
		try:
			qs = Department.objects.filter(name__icontains=words[0])
			for i in range(1, len(words)):
				qs = qs.filter(name__icontains=words[i])
			
			if len(qs) > 0:
				depts = []
				dl = []
				for d in qs:
					depts.append(d)
					a = '<a href="/depts/%s">%s</a>' % (d.dept, d.name)
					dl.append(a)
				dzipped = zip(depts, dl)
			else:
				errors = errors + "I don't feel like explaining"
		except Exception as inst:
			errors = errors + "\nDepartment options error: %s %s" % (type(inst), inst)
		
		if len(czipped) + len(pzipped) + len(dzipped) == 1:
			if len(czipped) == 1:
				c = czipped[0][0]
				cn = c.coursenum_set.all().order_by('dept__dept')[0]
				return HttpResponseRedirect("/courses/%s%s" % (cn.dept.dept, cn.number))
			
			if len(pzipped) == 1:
				p = pzipped[0][0]
				return HttpResponseRedirect("/profs/%s" % (p.netid))
			
			if len(dzipped) == 1:
				d = dzipped[0][0]
				return HttpResponseRedirect("/depts/%s" % (d.dept))
		
		all_depts = Department.objects.all().order_by('dept')

		if (czipped or pzipped or dzipped):
			t = get_template('search_results.html')
			html = t.render(Context({'courses':czipped, 'profs':pzipped, 'depts':dzipped, 'query':query, 'user':user, 'alldepts':all_depts}))
			return HttpResponse(html)			
				
		#errors = "Sorry we're not sure what you meant by: %s\n\n" % q + errors
		#return HttpResponse(errors)
		return HttpResponse(errors)
		t = get_template('search_empty.html')
		return HttpResponse(t.render(Context({'user':user, 'q':q, 'alldepts':all_depts})))
	
	all_depts = Department.objects.all().order_by('dept')			
	t = get_template('search_empty.html')
	return HttpResponse(t.render(Context({'user':user, 'q':'', 'alldepts':all_depts})))