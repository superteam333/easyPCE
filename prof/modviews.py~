from django.http import HttpResponse
from django.template import Context, loader
from pce.models import *
# Create your views here.

#from pce.models import Professor_Dept, Professor, Course_Instance

# Adapted from Luke Paulsen's code.
def check_login(request, redirect):
#   if request.session['netid'] == 'ejamnik':
#       return HttpResponse("JAMNIK SUCKS")
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

def professor(request, netid):
	try:
		n = request.session['netid']  
		if n == 'nweires' or n == 'jmtang' or n == 'lpaulsen' or n == 'gdisco' or n == 'apthorpe':
			return HttpResponse("Sorry, only open to beta testers")
		if request.session['netid'] is None:
			return check_login(request, "/profs/%s" % netid)
	except:
		return check_login(request, "/profs/%s" % netid)
	try:
		thisprofessor = Professor.objects.get(netid=netid)
	except Professor.DoesNotExist:
		thisprofessor=None
	template = loader.get_template('prof.html')
	if thisprofessor is not None:
                try:
                        courseQuerySets = []
                        preuniquecourses = []
			uniquecourses = []
#			courses = Course.objects.filter(profs__id=professor.id).order_by('coursenum__dept', 'coursenum__number','semester').distinct()
#			for course in courses:
#				uniquecourses.extend(CourseNum.objects.filter(instance=course))
			preuniquecourses = CourseNum.objects.filter(instance__profs__id=thisprofessor.id).distinct().order_by('dept__dept', 'number')
                        for p in preuniquecourses:
                            temp = True
                            cs = Course.objects.filter(coursenum=p)
                            for c in courseQuerySets:
                                if cs==c:
                                    temp = False
                            if temp:
                                uniquecourses.append(p)                                    
                            courseQuerySets.append(cs)
                            
			allCourses = []
                        if uniquecourses:
                            for c in uniquecourses:
                                query=Course.objects.filter(coursenum=c, profs__id=thisprofessor.id).order_by('-year', '-semester')
                                if query:
                                    allCourses.append(query[0])
			allCourses = []
			advice = []
			evaluation = []
			mostrecent=[]
			for u in uniquecourses:
                            for i, cors in enumerate(allCourses):
                                year = '2007-2008'
                                sem = 'Fall'
						
                                if (int(year[:4]) < int(cors.year[:4])) or ((sem == 'Fall') and (cors.semester == 'Spring') and (int(year[:4]) == int(cors.year[:4]))):
                                    if (int(cors.year[:4]) != 2013):
		
                                        advice.insert(i, Advice.objects.filter(instance=cors).order_by('length').reverse())
                                        evaluation.insert(i, Evaluation.objects.filter(instance=cors))
                                        mostrecent.insert(i, cors)
                                        sem = cors.semester
                                        year = cors.year

		except CourseNum.DoesNotExist:
			uniquecourses = []
                        allCourses = []
		try:
			departments = Department.objects.filter(professor=thisprofessor).order_by('name')
		except Department.DoesNotExist:
			departments = []
		try:
			bestcourses = CourseNum.objects.filter(bestprof=thisprofessor)
		except CourseNum.DoesNotExist:
			bestcourses = []
	
		zipped = zip(uniquecourses, mostrecent, advice, evaluation)
		c = Context({'prof':thisprofessor, 'unique':uniquecourses, 'depts':departments, 'best':bestcourses, 'list':zipped})
		html = template.render(c)
		return HttpResponse(html)
	else:
		professor = []
	c = Context({'prof':thisprofessor, 'unique':uniquecourses, 'depts':departments, 'best':bestcourses})
	html = template.render(c)
	return HttpResponse(html)

	#current = Professor.objects.filter(netid=netid)[0]
	#if (current is not None):
	#	uniquecourses = Course_Instance.objects.filter(prof=current).order_by('course.dept.name', 'course.number','semester').course.distinct()
	#	instances = Course_Instance.objects.filter(prof=current).order_by('course.dept.name', 'course.number','semester')
	#	depts = Professor_Dept.objects.filter(prof=current).order_by('dept.name')
	#else:
	#	uniquecourses = None
	#	instances = None
	#	depts = None
	#template = loader.get_template('professor.html')
	#c = Context({'uniquecourses'=uniquecourses, 'instances'=instances, 'depts'=depts})
	#return HttpResponse(template.render(c))
