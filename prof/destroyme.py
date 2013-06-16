import sys
sys.path.append('/srv/www/myapp/')
from myapp import settings
from django.core.management import setup_environ
setup_environ(settings)


from django.http import HttpResponse
from django.template import Context, loader
from pce.models import *
# Create your views here.

#from pce.models import Professor_Dept, Professor, Course_Instance

def professor(netid):
	try:
		thisprofessor = Professor.objects.get(netid=netid)
	except Professor.DoesNotExist:
		thisprofessor=None
	if thisprofessor is not None:
		try:
			uniquecourses = []
#			courses = Course.objects.filter(profs__id=professor.id).order_by('coursenum__dept', 'coursenum__number','semester').distinct()
#			for course in courses:
#				uniquecourses.extend(CourseNum.objects.filter(instance=course))
			uniquecourses = CourseNum.objects.filter(instance__profs__id=thisprofessor.id).distinct().order_by('dept__dept', 'number')
			
			allCourses = []
			advice = []
			evaluation = []
			mostrecent=[]
			for u in uniquecourses:
				try:
					allCourses = Course.objects.filter(coursenum=u, profs__id=thisprofessor.id)
					print u
					for c in allCourses:
						print c
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
				except Course.DoesNotExist:
					allCourses = []
		except CourseNum.DoesNotExist:
			uniquecourses = []
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

	else:
		professor = []
		c = Context({'prof':thisprofessor, 'unique':uniquecourses, 'depts':departments, 'best':bestcourses})
	print uniquecourses
	print ""
	print zipped
#	for u, mr, ads, evs in zipped:
#		print u
#		print str(mr.year) + " " + str(mr.semester)
#		print str(mr.profs)
#		print ads
#		print evs
	print ""
professor('gpop')
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
