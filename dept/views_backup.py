# Create your views here.
from django.http import HttpResponse
from django.template import loader as loader
#from pce.models import Department, Professor

def dephome(request, dept):
	deplist = Department.objects.filter(dept = dept)
	if (len(deplist) > 0):
		department = deplist[0]
	else:
		department = None
	if (department is not None):
		professors = Professor_Dept.objects.filter(dept = department).order_by('prof.lastname', 'prof.firstname')
		courses = Course.objects.filter(dept=department).order_by('dept.name', 'number')
	else:
		professors = None
		course = None
	template = loader.get_template('home.html')

	c = Context({'dept': department, 'prof':professors, 'cour':courses})
	return HttpResponse(template.render(c))

def depcourses(request, dept):

	deplist = Department.objects.filter(dept = dept)
	if (len(deplist) > 0):
		department = deplist[0]
	else:
		department = None
	if department is not None:
		professors = Professor_Dept.objects.filter(dept = department).order_by('prof.lastname', 'prof.firstname')
		courses = Course.objects.filter(dept=department).order_by('dept.name', 'number')
	else:
		professors = None
		course = None
	template = loader.get_template('courses.html')
	c = Context({'dept': department, 'prof':professors, 'cour':courses})
	return HttpResponse(template.render(c))

def depprofs(request, dept):
	deplist = Department.objects.filter(dept = dept)
	if (len(deplist) > 0):
		department = deplist[0]
	else:
		department = None
	if department is not None:
		professors = Professor_Dept.objects.filter(dept = department).order_by('prof.lastname', 'prof.firstname')
		courses = Course.objects.filter(dept=department).order_by('dept.name', 'number')
	else:
		professors = None
		course = None
	template = loader.get_template('professors.html')
	c = Context({'dept': department, 'prof':professors, 'cour':courses})
	return HttpResponse(template.render(c))

