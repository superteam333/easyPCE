# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.template import loader
from django.template import Context
from pce.models import Department as Department
from pce.models import Course as Course
from pce.models import Professor
from pce.models import CourseNum
from pce.models import User
from pce.models import Favorite
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
import _ssl;_ssl.PROTOCOL_SSLv23 = _ssl.PROTOCOL_SSLv3
import urllib, re

REGIS_PREFIX = "http://registrar.princeton.edu/course-offerings/search_results.xml?term=1142&subject="

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


@csrf_exempt
#@cache_control(no_cache=True, no_store=True)
def dephome(request, dept):
	global REGIS_PREFIX
	# Need to fix login
	if not settings.DEBUG:
		try:
			n = request.session['netid']  
			if request.session['netid'] is None:
				return check_login(request, '/depts/dept')
		except:
			return check_login(request, '/depts/dept')
		netid = request.session['netid']
	else:
		netid = 'dev'
	try:
	    user= User.objects.get(netid=netid)
	except:
		user=User(netid=netid)
		user.save()

	template = loader.get_template('dept.html')
	alldepts=Department.objects.all().order_by('dept')
	favs=Favorite.objects.filter(user=user)
	regNums=[]
	for i in range(len(favs)):
		regNums.append(favs[i].course.regNum)
	try:
		department = Department.objects.get(dept=dept.upper)
	except Department.DoesNotExist:
		department=[]
		regNums = []
		courses= []
		dept= []
		profs= []
		titles= []
		url= []
		c = Context({'user':user,'favorites':favorites, 'alldepts':alldepts, 'dept':department,'regNums':regNums, 'courses':courses, 'url':dept, 'profs':profs, 'titles':titles, 'registrarurl':url})
		return HttpResponse(template.render(c))
	if department is not None:
		url = REGIS_PREFIX + department.dept
		try:
			precourses = CourseNum.objects.filter(dept__dept=dept).order_by('number')
			courses = [] #this precourses courses old courses junk handles sorting by next year
			oldCourses = []
			for c in precourses:
				sems = Course.objects.filter(coursenum__id=c.id).order_by('-year', '-semester')
				if sems:
					if sems[0].year=="2013-2014" and sems[0].semester=="Spring":
						courses.append(c)
					else:
						oldCourses.append(c)
			for c in oldCourses:
				courses.append(c)
		except CourseNum.DoesNotExist:
			courses=[]
		if courses:
			profs = Professor.objects.filter(depts__dept=dept).order_by('lastname')
		else:
			profs = []
	else:
		url = None
		courses = None
		profs = []
	titles=[]
	instances=[]
	if courses:
		for i in range(len(courses)-1):
			query=Course.objects.filter(coursenum__id=courses[i].id).order_by('-year', '-semester')
			
			if query:
				instances.append(query[0])
	titles = zip(courses, instances)
	isFavorite=[]
	results=None
	for i in range(len(instances)):
		#results = Favorite.objects.get(user=user,course=instances[i])
		if results is None:
			isFavorite.append(False)
		else:
			isFavorite.append(True)
	favorites = zip(titles, isFavorite)	
	c = Context({'user':user,'favorites':favorites, 'alldepts':alldepts, 'dept':department,'regNums':regNums, 'courses':courses, 'url':dept, 'profs':profs, 'titles':titles, 'registrarurl':url})
	return HttpResponse(template.render(c))
