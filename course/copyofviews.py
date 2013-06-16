# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from pce.models import *
from sets import Set
# Create your views here.

#from pce.models import Course, Course_Instance

def course(request, subj, num):
	try:
		num = CourseNum.objects.get(dept__dept=subj, number=num)
	except CourseNum.DoesNotExist:
		num=None
	if num is None:
		courses=None
	else:
		try:
			courses = Course.objects.filter(coursenum__id=num.id).order_by('-year', '-semester')
		except Course.DoesNotExist:
			courses=None
	coursenum=[]
	coursenums=[]
	depts=[]
	unique=[]
	if courses is not None:
		coursenum=CourseNum.objects.filter(instance__regNum=courses[0].regNum)
	for i in range(len(coursenum)):
		depts.append(coursenum[i].dept)
	for i in range(len(depts)):
		if not depts[i] in depts[0:i]:
			unique.append(i)
	#make new coursenums that only adds it if it has unique
	for i in range(len(unique)):
		coursenums.append(str(coursenum[unique[i]]))
	coursenums=Set(coursenums)
	advice=[]
	evaluation=[]
	profs=[]
	if courses is not None:
		ran = len(courses)
		for i, cors in enumerate(courses):
			advice.append(Advice.objects.filter(instance=cors))
			evaluation.append(Evaluation.objects.filter(instance=cors))
	list = zip(courses, advice)
	con=Context({'course':courses, 'list':list, 'advices':advice,'evals':evaluation, 'coursenums':coursenums})
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

