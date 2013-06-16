# I guess this file was used to make sure professors had all the departments they were supposed
# to be connected to?

import operator
import sys
sys.path.append('/srv/www/myapp/')
from myapp import settings
from django.core.management import setup_environ
setup_environ(settings)
from models import *

profs = Professor.objects.all()
ps = len(profs)
for i, p in enumerate(profs):
    print str(i) + " out of " + str(ps)
    print "Looking at prof: " + str(p)
    try:
        depts = Department.objects.filter(professor=p)
        print "Already has:"
        for d in depts:
            print d
    except:
        continue
    try:
        cn = CourseNum.objects.filter(instance__profs__id=p.id)
        for c in cn:
            sys.stdout.write(str(c) + " ")
            for d in depts:
                print "COMPARING DEPTS " + str(c.dept.dept) + " " + str(d.dept)
#                print (c.dept.dept == d.dept)
                print (c.dept.dept != d.dept)
                if (c.dept.dept != d.dept):
                    print "adding:" + str(c.dept)
                    p.depts.add(c.dept)
                    p.save()
    except:
        continue

    print""
    
            
            
            
    
