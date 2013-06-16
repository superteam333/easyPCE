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
                allCourseNums = CourseNum.objects.filter(instance__profs__id=thisprofessor.id).distinct().order_by('dept__dept', 'number')
                mostRecentCourses = []
                courseRegNums = []
                uniqueCourseNums = []
                for cn in allCourseNums:
                    temp = True
                    j = 0
                    query = Course.objects.filter(coursenum=cn, profs__id=thisprofessor.id).order_by('-year', '-semester')
                    for i, rn in enumerate(courseRegNums):
                        if rn=query.regNum:
                            temp = false
                            j = i
                    if temp:
                        courseRegNums.append(query.regNum)
                        uniqueCourseNums.append([cn])
                        mostRecentCourses.append(query[0])
                    else:
                        uniqueCourseNums[j].append(cn)

                for i, cors in enumerate(mostRecentCourses):
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
                allCourseNums = []
                mostRecentCourses = []
            try:
                departments = Department.objects.filter(professor=thisprofessor).order_by('name')
            except Department.DoesNotExist:
                departments = []
            try:
                allBestcourses = CourseNum.objects.filter(bestprof=thisprofessor)
                bestRegNums = []
                uniqueBestcourse = []
                for cn in allBestcourses:
                    temp = True
                    j = 0
                    query = Course.objects.filter(coursenum=cn, profs__id=thisprofessor.id).order_by('-year', '-semester')
                    for i, rn in enumerate(bestRegNums):
                        if rn=query.regNum:
                            temp = false
                            j = i
                    if temp:
                        bestRegNums.append(query.regNum)
                        uniqueBestcourse.append([cn])
                    else:
                        uniqueBestcourse[j].append(cn)
            except CourseNum.DoesNotExist:
                uinqueBestcourse = []
	
            zipped = zip(uniqueCourseNums, mostrecent, advice, evaluation)
            c = Context({'prof':thisprofessor, 'unique':uniqueCourseNums, 'depts':departments, 'best':uinqueBestcourse, 'list':zipped})
            html = template.render(c)
            return HttpResponse(html)
	else:
            thisprofessor = []
            uniqueCourseNums = []
            departments = []
            uniqueBestcourse = []
            zipped = []
            c = Context({'prof':thisprofessor, 'unique':uniqueCourseNums, 'depts':departments, 'best':uniqueBestcourse, 'list':zipped})
            html = template.render(c)
            return HttpResponse(html)
