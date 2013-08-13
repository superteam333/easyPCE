# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.template import Context, loader
from django.template.loader import get_template
from pce.models import *
from django.core.cache import cache
import urllib, re
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

def ranking(request):
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
    alldepts = Department.objects.all().order_by('dept')
    favorites = []
    try:
        num = CourseNum.objects.get(dept__dept=subj, number=num)
        favs=Favorite.objects.filter(user=user)
        for f in favs:
            for cn in CourseNum.objects.filter(instance=f.course):
                if cn==num:
                    favorites.append(cn)
    except:
        pass

    cns = cache.get("BAYES_CNS")
    if not cns:
	    cns = CourseNum.objects.exclude(bayes__isnull=True).order_by('-bayes')[:500]
	    cache.set("BAYES_CNS", cns)
    cs = cache.get("BAYES_COURSES")
    if not cs:
	    cs = []
	    for cn in cns:
		    c = Course.objects.filter(coursenum=cn).order_by('-year', '-semester').only("regNum", "pdf", "nopdf", "da", "title")[:500]
		    cs.append(c[0])
	    cache.set("BAYES_COURSES", cs)
    regNums=[]
    favs=Favorite.objects.filter(user=user)
    for i in range(len(favs)):
        regNums.append(favs[i].course.regNum)
    bayeszip = zip(cns, cs)
    c = Context({'user':user, 'alldepts':alldepts, 'favorites':favorites, 'bayes':bayeszip, 'regNums':regNums})
    t = get_template("rankings.html")
    return HttpResponse(t.render(c))
