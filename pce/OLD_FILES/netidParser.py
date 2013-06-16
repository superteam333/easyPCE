# This is a parser for netid data. John Whelchel.                       
import os
import re
import sys
sys.path.append('/srv/www/myapp/')
from myapp import settings
from django.core.management import setup_environ
setup_environ(settings)
from models import *


PATH = "/home/ubuntu/registrar_scrape/allNetIDSfinal.txt"

def exists(testnetid, p):
    try:
        prof = Professor.objects.filter(netid=testnetid)
        if len(prof) > 0:
            return testnetid + str(p.pk)
        else:
            return testnetid
    except Professor.DoesNotExist:
        return testnetid

def clearNetIDS():
    allprofs = Professor.objects.all()
    for prof in allprofs:
        prof.netid = ""
        prof.save()

def getNetIDS():
#    f = open(PATH, 'r')
#     for line in f:
#        firstname = []
#        words = line.split()
#        lastWord = ""
#        for i, word in enumerate(words):
#            res = re.search("\(.*\)", word)
#            if res is None:
#                firstname.append(word)
#            else:
#                netid = word.strip('()')
#               print netid
#               lastname = lastWord
#               break;
#           lastWord = word
#        if len(firstname) != 0:
#            firstname.pop()
#        name = ""
#        for i, word in enumerate(firstname):
#            if i == 0:
#                name = name + word
#            else:
#                name = name + " " + word
#        print "The first name is " + name
#        try:
#            prof = Professor.objects.get(firstname=name,
#                                         lastname=lastname)
#            print "This guy matched " + str(prof)
#            if prof.netid == "":
#                prof.netid = netid;
#                prof.save()
#        except Professor.DoesNotExist:
#            print "this guy didn't match " + name + " " + lastname
    allprofs = Professor.objects.all()
    for prof in allprofs:
        fakenetid = ""
        if prof.netid == "":
            fakenetid = prof.firstname.replace(" ", "").replace(".","").lower() + prof.lastname.replace(" ", "").replace(".","").lower()
            fakenetid = exists(fakenetid, prof)
            prof.netid = fakenetid
            if fakenetid is None:
                print prof
#            print fakenetid + " is our fake"
            prof.save()
        
#clearNetIDS()
getNetIDS()

