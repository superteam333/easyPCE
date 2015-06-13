# This is a parser for registar json data. John Whelchel.
# COS 333 Final Project Spring 2013
import json
import os
import re
import sys
sys.path.append('/srv/www/myapp/')
from myapp import settings
from django.core.management import setup_environ
setup_environ(settings)
from pce.models import *

DIR_PATH = '/srv/www/myapp/easypce_datatools/registrar_scrape/DATA/DATA_FALL_2014_2015/'
VERBOSE = True
FILECOUNT = 0

def v(data):
    if VERBOSE:
        print data

class Parser:


    SAVE_FILE = "state_of_parser.json"

    def __init__(self):
        self.data = {}
        self.state = {}

    def save(self):
        f = open(Parser.SAVE_FILE, 'w')
        if f == None:
            v("Can't create/open file for saving state")
            return False
        json.dump(self.state, f)
        f.close()
        return True

    def load(self):
        try:
            f = open(Parser.SAVE_FILE, 'r')
            if f == None:
                v("Can't open file")
                return False
            self.state = json.load(f)
            f.close()
            v("Loaded data\n")
            return True
        except IOError:
            return False
    

    def saveCourse(self, filename):

        # FOR MODELS< COURSE ID AND TERM CAN RECONSTRUCT LINK TO REGISTRAR
        f = open(filename)
        try:
            data = json.load(f)
        except ValueError:
            print "The borken file is " + filename
        info = data[0]
        m = re.search(r'Spring', filename)
        if m is None:
            sem = 'Fall'
        else:
            sem = 'Spring'
        m = re.search(r'....-....', filename)
        if m is None:
            print "We got problems son. Looks like no year in file."
            return
        year = m.group(0)

        for listing in info['listings']:
            # see if dept in db
            try:
                d = Department.objects.get(dept=listing['dept'])
            except Department.DoesNotExist:
                d = Department(dept=listing['dept'])
                d.save()

        cnums = []
        newcnums = []
        for listing in info['listings']:
             #see if coursenum in db, probably isn't ???                                            
            try:
                cn = CourseNum.objects.get(dept=Department.objects.get(dept=listing['dept']),
                                           number=listing['number'])
                if cn:
                    cnums.append(cn)
                    continue
            except CourseNum.DoesNotExist:
                newcn = CourseNum(dept=Department.objects.get(dept=listing['dept']),
                                  number=listing['number'])
                newcnums.append(newcn)
                newcn.save()


        
        try:
            course = Course.objects.get(title=info['title'],
                           regNum=info['courseid'],
                           description=info['descrip'],
                           semester=sem,
                           year=year)
            print "Course already exists"
            return
        except Course.DoesNotExist:
            ourcourse = Course(title=info['title'],
                           regNum=info['courseid'],
                           description=info['descrip'],
                           semester=sem,
                           year=year)
            ourcourse.save()
            global FILECOUNT
            FILECOUNT = FILECOUNT + 1
            if FILECOUNT % 1000 == 1:
                print FILECOUNT
            for cn in cnums:
                cn.instance.add(ourcourse)
            for cn in newcnums:
                cn.instance.add(ourcourse)
        
    
        pidb = []
        pnotidb = []

        for prof in info['profs']:
            #see if profs in database
            first = ""
            try:
                names = prof['name'].split()
                if len(names) > 2:
                    for i in range(len(names)):
                        if i == len(names) - 1:
                            break
                        if i == 0:
                            first = names[i]
                        else:
                            first = first + " " + names[i]
                    last = names[len(names) - 1]
                else:
                    first = names[0]
                    last = names[1]
                pro  = Professor.objects.get(firstname=first.replace(",",""),
                                             lastname=last.replace(",",""))
                if pro:
                    pidb.append(pro)
            except Professor.DoesNotExist:
                yo = [first, last]
                pnotidb.append(yo)
        
        for prof in pnotidb:

            #add ones not in db to db
            p = Professor(firstname=prof[0].replace(",",""), lastname=prof[1].replace(",",""))
            p.save()
            ourcourse.profs.add(p)
            for listing in info['listings']:
                p.depts.add(Department.objects.get(dept=listing['dept']))
                
        #add depts to profs who need it
        for prof in pidb:    
            ourcourse.profs.add(prof)
            for listing in info['listings']:
                departs = prof.depts.filter(dept=listing['dept'])
                if not departs:
                    continue
                else:
                    prof.depts.add(Department.objects.get(dept=listing['dept']))
                        


        #for prof in info['profs']:
        #    print prof['name']
        #print info['title']
        #print info['courseid']
        #for listing in info['listings']:
        #    print listing['dept'], listing['number']
        #print info['descrip']
        #print info['classnum'] buried on layer deeper at classes


    def skipAhead(self, files):
        if len(self.state) != 0:
            foundPlace = False;
            newfiles = []
            for file in files:
                if foundPlace:
                    newfiles.extend(file)
                if file is self.state:
                    foundPlace = True;
            return newfiles
        else:
            return files

    def parse_dir(self):

        path = DIR_PATH
        files = os.listdir(path)
        for i, file in enumerate(files):
            files[i] = path + file

        files = self.skipAhead(files)

        for file in files:
            v("Operating on file:" + file + '\n')
            self.saveCourse(file)
            self.state = file
            #self.save()
        v("Files are all parsed.")
        return True

p = Parser()
if(not p.load()):
    print "Unable to load file, starting from scratch"
if(p.parse_dir()):
    print "Hooray, we're done!"
else:
    print "Uh oh"
