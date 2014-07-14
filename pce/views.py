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
	nums=Course.objects.filter(regNum=regNum).order_by('-year', '-semester')
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
	if request.method == 'GET':
		netid=request.session['netid']
	
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
			nums=sorted(set(nums))
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
	try:
		if request.session['netid'] is None:
			return check_login(request, '/favorites')
	
		netid = request.session['netid']
	except:
                return check_login(request, '/')
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
			nums=sorted(set(nums))
			allnums.append(nums)
			urls.append(str(coursenums[unique[0]]).strip(' '))
			
			matches = Course.objects.filter(id=favorites[i].course.id).order_by('-year', '-semester')
			try:
				if matches[0].year=='2013-2014' and matches[0].semester=='Fall':
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
