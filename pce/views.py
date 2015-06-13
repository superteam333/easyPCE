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

def pop(request):
	t = get_template("temp.html")
	return HttpResponse(t.render(Context({})))

def getBayes():
	bayes = []
	bayesCN = []
	f = open(os.path.join(os.path.dirname(__file__), "25ratings.txt"), "r")
	for l in f:
		w = l.split()
		d = Department.objects.get(dept=w[0])
		c = CourseNum.objects.get(dept=d, number=w[1])
		cc = Course.objects.filter(coursenum=c).order_by('-year', '-semester')
		bayesCN.append(c)
		bayes.append(cc[0])
	zipped = zip(bayes, bayesCN)
	return zipped

# Adapted from Luke Paulsen's code.
def check_login(request, redirect):
	cas_url = "https://fed.princeton.edu/cas/"
	service_url = 'http://' + urllib.quote(request.META['HTTP_HOST'] + request.META['PATH_INFO'])
	service_url = re.sub(r'ticket=[^&]*&?', '', service_url)
	service_url = re.sub(r'\?&?$|&$', '', service_url)
	if "ticket" in request.GET:
		val_url = cas_url + "validate?service=" + service_url + '&ticket=' + urllib.quote(request.GET['ticket'])
		r = urllib.urlopen(val_url).readlines() #returns 2 lines
		if len(r) == 2 and re.match("yes", r[0]) != None:
			request.session['netid'] = r[1].strip()
			return HttpResponseRedirect(redirect)
		else:
			return HttpResponse("FAILURE")
	else:
		login_url = cas_url + 'login?service=' + service_url
		return HttpResponseRedirect(login_url)

def autotest(request):
	t = get_template("autotest.html")
	c = Context({})
	return HttpResponse(t.render(c))

def login_page(request):
	try: # ADDED TRY HERE... ORIGINAL IN WHAT IS GOING ON... SEEMED TO FIX IT. 1 of 2
		if request.session['netid'] is None:
			return check_login(request, '/')
	except:
		return check_login(request, '/')
	netid = request.session['netid']
	return HttpResponse(netid)

def logout(request):
	request.session['netid'] = None
	return HttpResponseRedirect("https://fed.princeton.edu/cas/logout")
	
def hello(request):
	return HttpResponse("hello world")

def induce(request):
	if not settings.DEBUG:
		try: # ADDED TRY HERE... ORIGINAL IN WHAT IS GOING ON... SEEMED TO FIX IT. 2 of 2            
			n = request.session['netid']
			if request.session['netid'] is None:
				return check_login(request, '/')
		except:
			return check_login(request, '/')
		netid = request.session['netid']
	else:
		netid = 'dev'
	alldepts=Department.objects.all().order_by('dept')
	try:
		user= User.objects.get(netid=netid)
	except:
		user=User(netid=netid)
		user.save()
	t = get_template("induce.html")
	depts = Department.objects.all().order_by('dept')
	c = Context({'depts':depts, 'user':user, 'alldepts':alldepts})
	return HttpResponse(t.render(c))

@csrf_exempt
def editfavorites(request):
	if request.method == 'POST':
		data=request.POST
		dict=data.dict()
	string=dict['string']
	#query=QueryDict(string).dict()
	query=QueryDict(string).dict()
	regNum=query['regNum'].strip('row')
	try:
		user=User.objects.get(netid=query['user'])
	except:
		user=User(netid=query['user'])
		user.save()

	"""
	here we made a messy fix. basically in some palces the row ids weren't the registrar
	number and I didn't pass an extra thing to the contexts. So instead in those cases, for regnum, 
	I put in the title of the class. if the query with that regnum comes up empty then 
	I search for the first course with that the course dept and number
	"""
	try:
		nums=Course.objects.filter(regNum=regNum).order_by('-year', '-semester')
	except:
		##course num parsing
		department = regNum[:3]
		number = int(regNum[3:])
		num = CourseNum.objects.get(dept__dept=department, number=number)
		nums=Course.objects.filter(coursenum__id=num.id).order_by('-year', '-semester')

	add=int(query['add'])
	#favorite a coursenum not a course
	if add is 1:
		try:
			fav = Favorite.objects.get(user=user, course=nums[0])
		except:
			fav = Favorite(user=user, course=nums[0])
			fav.save()
	else:
		for n in nums:
			cns = CourseNum.objects.filter(instance=n)
			for c in cns:
				cs = Course.objects.filter(coursenum=c)
				for k in cs:
					try:
						fav = Favorite.objects.get(user=user, course=k)
						fav.delete()
					except:
						pass
	#dict=q.dict()
	#new=User(netid=dict['regNum'])
	#new.save()
	return HttpResponse("haha")
		
def getfavorites(request):
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

	try:
		favorites=Favorite.objects.filter(user=user)
	except:
		favorites=None                 
	allnums=[]	
	urls=[]
	if favorites is not None:
		for i in range(len(favorites)):
			unique=[]
			coursenums=[]
			depts=[]
			nums=[]
			coursenums=CourseNum.objects.filter(instance=favorites[i].course)
			for i in range(len(coursenums)):
				depts.append(coursenums[i].dept)
			for i in range(len(depts)):
				if not depts[i] in depts[0:i]:
					unique.append(i)
			for i in range(len(unique)):
				nums.append(str(coursenums[unique[i]]))
			nums=sorted(Set(nums))
			allnums.append(nums)
			url = str(coursenums[unique[0]])
			url = re.sub('\s', '', url)
			urls.append(url)
			#urls.append(' ')
	data=[]
	zipped=zip(favorites, allnums, urls)
	for fav, nums, url in zipped:
		string=''
		string=string+str(nums[0])	
		for s in nums[1:]:
			string=string+' / ' + str(s)
		current=[]
		current.append(string)
		current.append(str(fav.course))
		current.append(url)
		data.append(current)
	json=simplejson.dumps(data)	
	return HttpResponse(json, mimetype='application/json')
	 
def favorites(request):
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

	alldepts=Department.objects.all().order_by('dept')
	user=None
	try:
	    user= User.objects.get(netid=netid)
	except:
	    user=User(netid=netid)
	    user.save()	            	                                        	
	try:
		favorites = Favorite.objects.filter(user=user)                        
	except:
		favorites=None
	allnums=[]
	urls=[]
	nextSemester=[] #1 if available next semester and 0 if not
	matches=[]
	scores=[]
	if favorites is not None:
		for i in range(len(favorites)):
			unique=[]
			coursenums=[]
			depts=[]
			nums=[]
			coursenums=CourseNum.objects.filter(instance=favorites[i].course)
			scores.append(coursenums[0].avg)
			for j in range(len(coursenums)):
				depts.append(coursenums[j].dept)
			for k in range(len(depts)):
				if not depts[k] in depts[0:k]:
					unique.append(k)	
			for l in range(len(unique)):
			    nums.append(str(coursenums[unique[l]]))
			nums=sorted(Set(nums))
			allnums.append(nums)
			urls.append(str(coursenums[unique[0]]).strip(' '))
			
			matches = Course.objects.filter(id=favorites[i].course.id).order_by('-year', '-semester')
			try:
				if matches[0].year=='2013-2014' and matches[0].semester=='Spring':
					nextSemester.append(1)
				else:
					nextSemester.append(0)
			except:
				nextSemester.append(0) 
	t = get_template("myfavorites.html")
	zipped=zip(favorites, allnums, urls, scores, nextSemester)

	c = Context({'favorites':favorites, 'nextSemester':nextSemester, 'zip':zipped, 'alldepts':alldepts, 'user':user})
	return HttpResponse(t.render(c))

def test(request):
	s = ""
	for i in range(3):
		s = "%s\cCategory %s" % (s, i)
		for j in range(5):
			s = "%s\nOption %s" % (s, j)
	
	#s2 = ''.join([`num`+'/c' for num in xrange(5000)])
	module_dir = os.path.dirname(__file__)
	file_path = os.path.join(module_dir, 'autodata')
	f = open(file_path)
	s2 = f.read()
	return HttpResponse(s2)
		

def timeline(request):
	c = loader.get_template("timeline.html")
	con = Context({})
	return HttpResponse(c.render(con))

# Use this view with the accompanying URL to take the site down for maintenance.
def maintenance(request):
	try: # ADDED TRY HERE... ORIGINAL IN WHAT IS GOING ON... SEEMED TO FIX IT. 2 of 2                                                                                                                 
		n = request.session['netid']
		if request.session['netid'] is None:
			return check_login(request, '/')
	except:
		return check_login(request, '/')
	netid = request.session['netid']
	alldepts=Department.objects.all().order_by('dept')
	try:
		user= User.objects.get(netid=netid)
	except:
		user=User(netid=netid)
		user.save()

	template = loader.get_template("maintenance.html")
	c = Context({})
	return HttpResponse(template.render(c))

def index(request):
	if not settings.DEBUG:
		try: # ADDED TRY HERE... ORIGINAL IN WHAT IS GOING ON... SEEMED TO FIX IT. 2 of 2
			n = request.session['netid']
			if request.session['netid'] is None:
				return check_login(request, '/')
		except:
			return check_login(request, '/')
		netid = request.session['netid']
	else:
		netid = 'dev'
	alldepts=Department.objects.all().order_by('dept')
	try:
		user= User.objects.get(netid=netid)
	except:
		user=User(netid=netid)
		user.save()
	zipped = getBayes()
	template = loader.get_template("index.html")
	depts = Department.objects.all().order_by('dept')
	c = Context({'depts':depts, 'user':user, 'alldepts':alldepts, 'bayes':zipped})
	return HttpResponse(template.render(c))
	
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
						html = t.render(Context({'results':res,'query':q, 'user':user, 'alldepts':ds}))
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
						html = t.render(Context({'results':res,'query':q, 'user':user, 'alldepts':Department.objects.all().order_by('dept')}))
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
				set = Set([])
				unique = []
				numStrings = []
				results = ""
				for c in courses:
					nums = c.coursenum_set.all().order_by('dept__dept')
					numString = "%s" % nums[0]
					for a in range(1, len(nums)):
						numString = "%s / %s" % (numString, nums[a])
					if numString not in set:
						set.add(numString)
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
				return HttpResonseRedirect("/depts/%s" % (d.dept))
		
		all_depts = Department.objects.all().order_by('dept')

		if (czipped or pzipped or dzipped):
			t = get_template('search_results.html')
			html = t.render(Context({'courses':czipped, 'profs':pzipped, 'depts':dzipped, 'query':q, 'user':user, 'alldepts':all_depts}))
			return HttpResponse(html)			
				
		#errors = "Sorry we're not sure what you meant by: %s\n\n" % q + errors
		#return HttpResponse(errors)
		t = get_template('search_empty.html')
		return HttpResponse(t.render(Context({'user':user, 'q':q, 'alldepts':all_depts})))
	
	all_depts = Department.objects.all().order_by('dept')			
	t = get_template('search_empty.html')
	return HttpResponse(t.render(Context({'user':user, 'q':'', 'alldepts':all_depts})))
