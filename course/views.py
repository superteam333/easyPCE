# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.template import Context, loader
from pce.models import *
from sets import Set
import _ssl;_ssl.PROTOCOL_SSLv23 = _ssl.PROTOCOL_SSLv3 #why is this here?
import urllib, re

# Create your views here.

#from pce.models import Course, Course_Instance

termss = dict()
termss['Fall 2006-2007']=1072
termss['Fall 2007-2008']=1082
termss['Fall 2008-2009']=1092
termss['Fall 2009-2010']=1102
termss['Fall 2010-2011']=1112
termss['Fall 2011-2012']=1122
termss['Fall 2012-2013']=1132
termss['Fall 2013-2014']=1142
termss['Fall 2014-2015']=1152
termss['Spring 2006-2007']=1074
termss['Spring 2007-2008']=1084
termss['Spring 2008-2009']=1094
termss['Spring 2009-2010']=1104
termss['Spring 2010-2011']=1114
termss['Spring 2011-2012']=1124
termss['Spring 2012-2013']=1134
termss['Spring 2013-2014']=1144

REGIS_PREFIX = "http://registrar.princeton.edu/course-offerings/course_details.xml?courseid="
	
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
	
def course(request, subj, num):
	global termss, REGIS_PREFIX
	if not settings.DEBUG:
		try: # ADDED TRY HERE... ORIGINAL IN WHAT IS GOING ON... SEEMED TO FIX IT. 1 of 1           
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
	alldepts = Department.objects.all().order_by('dept')			
	favorites = []
	try:
		num = CourseNum.objects.get(dept__dept=subj, number=num)
		favs=Favorite.objects.filter(user=user)
		for f in favs:
			for cn in CourseNum.objects.filter(instance=f.course):
				if cn==num:
					favorites.append(cn)

	except CourseNum.DoesNotExist:
		coursesWithUpcoming = []
		zipped = []
		advice = []
		evaluation = []
		coursenums = [str(subj) + str(num)]
		profs = []
		bestprof = []
		num = str(subj) + str(num)
		url = []
		favNum = []
		con=Context({'course':coursesWithUpcoming, 'list':zipped, 'advices':advice,'evals':evaluation, 'coursenum':coursenums, 'profs':profs, 'best':bestprof, 'cn':num, 'registrarurl':url, 'user':user, 'alldepts':alldepts, 'inFav':favorites, 'favNum':favNum})
		template = loader.get_template('course.html')
		html = template.render(con)
		return HttpResponse(html)
	if num is None:
		courses=None
		regNum = None
		termNum=None
	else:
		bestprof = [] # can't we just end through the queryset?
		bestprofs = Professor.objects.filter(coursenum__id=num.id)
		for p in bestprofs:
			bestprof.append(p)
		try:
			courses = [] # can use slicing to make this better
			coursesWithUpcoming = Course.objects.filter(coursenum__id=num.id).order_by('-year', '-semester')
			for c in coursesWithUpcoming:
				courses.append(c)
				#if c.year!='2013-2014':
				#	courses.append(c)
			termNum = termss[str(coursesWithUpcoming[0].semester) + " " + str(coursesWithUpcoming[0].year)]
			regNum = str(coursesWithUpcoming[0].regNum)
		except Course.DoesNotExist:
			courses=None
	#isFavorite=None
	#try:
	#	isFavorite=Favorites.objects.get(user=user, course=courses[0])
	#except:
	#	isFavorite=None
	#if isFavorite is not None:
	#	favorite=True
	#else:
	#	favorite=False
	coursenum=[]
	coursenums=[]
	depts=[]
	unique=[]
	if courses is not None:
		if len(courses) > 0:
			coursenum=CourseNum.objects.filter(instance__regNum=courses[0].regNum)
	else:
		coursenums.append(str(num))
	for i in range(len(coursenum)):
		depts.append(coursenum[i].dept)
	for i in range(len(depts)):
		if not depts[i] in depts[0:i]:
			unique.append(i)
	#make new coursenums that only adds it if it has unique
	for i in range(len(unique)):
		coursenums.append(str(coursenum[unique[i]]))
	coursenums=sorted(Set(coursenums))
	advice=[]
	evaluation=[]
	profs=[]
	for i in range(0, len(courses)-1):
		if ((courses[i].year == '2013-2014') and (courses[i].semester == 'Spring')):
			courses.pop(i)
			
	for i in range(0, len(courses)-1):
		if courses[i].year == '2014-2015':
			courses.pop(i)
			break
	if courses is not None:
		ran = len(courses)
		for i, cors in enumerate(courses):
			advice.append(Advice.objects.filter(instance=cors).order_by('length').reverse())
			evaluation.append(Evaluation.objects.filter(instance=cors))
			profs.append(Professor.objects.filter(course=cors))
		
		zipped = zip(courses, evaluation, advice, profs)

	if termNum:
		url = REGIS_PREFIX + regNum.zfill(6) + '&term=' + str(termNum)
		favNum = regNum
	else:
		url = None
	con=Context({'course':coursesWithUpcoming, 'list':zipped, 'advices':advice,'evals':evaluation, 'coursenums':coursenums, 'profs':profs, 'best':bestprof, 'cn':num, 'registrarurl':url, 'user':user, 'alldepts':alldepts, 'inFav':favorites, 'favNum':favNum})
	template = loader.get_template('course.html')
	html = template.render(con)
	return HttpResponse(html)
	#try:
	#	c = Course.objects.filter(dept__dept=subj, number=num)
	#except Course.DoesNotExist:
	#	c=None
	#template = loader.get_template('course.html')
	#if c is not None:
	#	advice = []
	#	evaluation = []
	#	ran = len(c)
	#	for i, cors in enumerate(c):
	#		advice.extend(Advice.objects.filter(instance=cors))
	#		evaluation.extend(Evaluation.objects.filter(instance=cors))
	#	con = Context({'course':c, 'advices':advice, 'evals':evaluation, 'leng':ran})
	#	html = template.render(con)
	#	return HttpResponse(html)
	#con = Context({'course':c}, {'coursenum':num}, {'sub':subj})
	#html = template.render(c)
	#return HttpResponse(html)


	#current = Course.objects.filter(dept=subj, num=number)[0]
	#if current is not None:
	#	instances = Course_Instance.objects.filter(course=current).order_by('semester')
	#else:
	#	instances = None
	#template = loader.get_template('course.html')
	#c = Context({'course'=current, 'instances'=instances})
	#return HttpResponse(template.render(c))

