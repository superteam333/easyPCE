import argparse
from bs4 import BeautifulSoup
from bs4 import Tag
from collections import OrderedDict
import getpass
import json
import pycurl
import random
import re
import StringIO
import sys
import time
import urllib

# Modified by John Whelchel for COS 333 Final Project Spring 2013
# By Candy Button, Fall 2012 Independent Work with Brian Kernighan
# Much borrowed from http://www.angryobjects.com/2011/10/15/http-with-python-pycurl-by-example/

def checkLoop(url):
    return re.search("fromBrowserCheck=1", url);

def setCookie(c, cookie):
    c.setopt(c.COOKIE, cookie);
    
def getBaseURL(inURL):
    match = re.search("https://.*?/", inURL);
    if match == None:
        return None;
    return match.group(0)[0:-1];

def getRedirectURL(inURL):
    chunks = inURL.split("?");
    if (len(chunks) < 2): 
        return None;
    if not re.match(".+", chunks[1]): 
        return None;
    outURL = "";
    for i in range(1, len(chunks)):
        outURL += chunks[i];
        if i != len(chunks) - 1:
            outURL += "?"
    outURL += ("&" if (len(chunks) > 2) else "?");
    if checkLoop(inURL):
        outURL += "fromBrowserCheck=1";
    return outURL;

def v(text):
    if Curler.VERBOSE:
        print text;

class Curler:

    MAX_DELAY = 1
    SAVE_FILE = "state_of_curler.json"
    VERBOSE = False

    def __init__(self):
        self.formvals = None
        self.selects = None
        self.fileno = 0
        self.pycurler = None
        self.currentsoup = None
        self.fastforward = False

    def nextfilename(self):
        self.fileno += 1;
        return "page%d.html" % self.fileno;

    # function gowait()
    #   If tofile is true, this writes the response to a file. 
    #   If returnstring is true, it returns the response as a string.
    #   Both can be set, or one, or neither.
    def gowait (self, c, tofile, returnstring):
        buf = StringIO.StringIO();
        c.setopt(c.WRITEFUNCTION, buf.write);
        try:
            c.perform();
        except pycurl.error, error:
            errno, errstr = error
            print 'An error occurred: ', errstr
            buf.close();
            raise Exception("Error in gowait");

        response = buf.getvalue();
        buf.close();
        if tofile:
            self.writefile(response, None);

        rand = random.randint(1, Curler.MAX_DELAY)
        if not Curler.VERBOSE:
            print " .",
        v("Sleeping for %d seconds..." % rand);
        time.sleep(rand)
        if returnstring:
            return response;

    def writefile(self, text, filename):
        if filename == None:
            filename = self.nextfilename();
        f = open(filename, "w");
        f.write(text);
        f.close();        

    def loadformvals(self):
        try:
            f = open(Curler.SAVE_FILE, 'r')
            if f == None:
                return False
            self.formvals = json.load(f);
            f.close()
            v("******** LOADED FORM VALUES *******\n")
            return True
        except IOError:
            print "Failed loading form values; file %s not readable" % Curler.SAVE_FILE
            return False

    def saveformvals(self):
        f = open(Curler.SAVE_FILE, 'w')
        json.dump(self.formvals, f)
        f.close()

    def login(self):
        c = pycurl.Curl();
        self.pycurler = c;

        print "Logging in",
        v("##########################  Login page - username  #########################")
        c.setopt(c.URL, "https://puaccess.princeton.edu/oasa/loginPage.jsp");
        c.setopt(c.FOLLOWLOCATION, 1);        
        c.setopt(c.MAXREDIRS, 6);
        c.setopt(c.CONNECTTIMEOUT, 5)
        c.setopt(c.TIMEOUT, 12)
        c.setopt(c.USERAGENT, "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:14.0) Gecko/20100101 Firefox/14.0.1");
        c.setopt(c.COOKIEFILE, '')
        c.setopt(c.FAILONERROR, True)
        c.setopt(c.HTTPHEADER, ['Accept: text/html', 'Accept-Charset: UTF-8'])
        self.gowait(c, False, False);

        netid = urllib.quote_plus(raw_input('\n\nNetid: '));
        

        v("##########################  Login page - password  #########################")
        c.setopt(c.URL, 'https://puaccess.princeton.edu/oasa/login.do');
        c.setopt(c.POSTFIELDS, 'userid=' + netid);
        self.gowait(c, False, False);

        password = urllib.quote_plus(getpass.getpass("\n\nPassword: "));

        v("##########################  Score Options Page (Logged in)  #########################")
        c.setopt(c.URL, 'https://puaccess.princeton.edu/oasa/password.do');
        c.setopt(c.POSTFIELDS, "Bharosa_Password_PadDataField=" + password);
        self.gowait(c, False, False);

        # TODO: detect failure case (bad password) here, and quit

        # Can we delete this one? NO
        v("########################## Score Home Page #############################")
        c.setopt(c.URL, 'https://puaccess.princeton.edu/psp/hsprod/EMPLOYEE/HRMS/h/?tab=DEFAULT');
        c.setopt(c.HTTPGET, 1);
        self.gowait(c, False, False);

        v("########################## Score Home Page AJAX Menu #############################")
        c.setopt(c.URL, 'https://puaccess.princeton.edu/psp/hsprod/EMPLOYEE/HRMS/h/?cmd=getCachedPglt&pageletname=MENU&tab=DEFAULT&PORTALPARAM_COMPWIDTH=Narrow&ptlayout=N');
        c.setopt(c.HTTPGET, 1);
        self.gowait(c, False, False);

        v("########################## Score Home Page AJAX Student Center Box #############################")
        c.setopt(c.URL, 'https://puaccess.princeton.edu/psp/hsprod/EMPLOYEE/HRMS/h/?cmd=getCachedPglt&pageletname=ADMN_SC_PGT_SCORE&tab=DEFAULT&PORTALPARAM_COMPWIDTH=Wide&ptlayout=N');
        c.setopt(c.HTTPGET, 1);
        self.gowait(c, False, False);

        v("########################## Score Student Center #############################")
        c.setopt(c.URL, 'https://puaccess.princeton.edu/psp/hsprod/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL?PORTALPARAM_PTCNAV=HC_SSS_STUDENT_CENTER&EOPP.SCNode=HRMS&EOPP.SCPortal=EMPLOYEE&EOPP.SCName=ADMN_SCORE&EOPP.SCLabel=&EOPP.SCPTcname=ADMN_SC_SP_SCORE&FolderPath=PORTAL_ROOT_OBJECT.PORTAL_BASE_DATA.CO_NAVIGATION_COLLECTIONS.ADMN_SCORE.ADMN_S200801281459482840968047&IsFolder=false');
        c.setopt(c.HTTPGET, 1);
        self.gowait(c, False, False);

        v("########################## Score Student Center: iFrame #############################")
        c.setopt(c.URL, 'https://puaccess.princeton.edu/psc/hsprod/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL?PORTALPARAM_PTCNAV=HC_SSS_STUDENT_CENTER&EOPP.SCNode=HRMS&EOPP.SCPortal=EMPLOYEE&EOPP.SCName=ADMN_SCORE&EOPP.SCLabel=&EOPP.SCPTcname=ADMN_SC_SP_SCORE&FolderPath=PORTAL_ROOT_OBJECT.PORTAL_BASE_DATA.CO_NAVIGATION_COLLECTIONS.ADMN_SCORE.ADMN_S200801281459482840968047&IsFolder=false&PortalActualURL=https%3a%2f%2fpuaccess.princeton.edu%2fpsc%2fhsprod%2fEMPLOYEE%2fHRMS%2fc%2fSA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL&PortalContentURL=https%3a%2f%2fpuaccess.princeton.edu%2fpsc%2fhsprod%2fEMPLOYEE%2fHRMS%2fc%2fSA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL&PortalContentProvider=HRMS&PortalCRefLabel=Student%20Center&PortalRegistryName=EMPLOYEE&PortalServletURI=https%3a%2f%2fpuaccess.princeton.edu%2fpsp%2fhsprod%2f&PortalURI=https%3a%2f%2fpuaccess.princeton.edu%2fpsc%2fhsprod%2f&PortalHostNode=HRMS&NoCrumbs=yes&PortalKeyStruct=yes');
        c.setopt(c.HTTPGET, 1);
        self.gowait(c, False, False);

        v("########################## Course Evals Link (AJAX Response)  #############################")
        c.setopt(c.URL, 'https://puaccess.princeton.edu/psc/hsprod/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL');
        c.setopt(c.POSTFIELDS, 'ICAJAX=1&ICNAVTYPEDROPDOWN=1&ICType=Panel&ICElementNum=0&ICStateNum=1&ICAction=PU_DERIVED_SSR_PU_COURSE_EVAL_LK&ICXPos=0&ICYPos=0&ResponsetoDiffFrame=-1&TargetFrameName=None&GSrchRaUrl=None&FacetPath=None&ICFocus=&ICSaveWarningFilter=0&ICChanged=-1&ICResubmit=0&ICSID=OqpcsWdN%2FYsyi1CKPIXNW1RSIULhE%2FlkMnjUIy48EXo%3D&ICActionPrompt=false&ICFind=&ICAddCount=');
        response = self.gowait(c, False, True);

        # Ignoring the second AJAX request the browser sends here, for now (?)

        match = None;
        for line in response.split('\n'):
            if "window.open(" in line:
                match = re.search("'https://www\.applyweb\.com.*?'", response);
                if match: break;
        if match == None:
            raise Exception("Failed to open course eval page. Could be a bad username/password?");

        applyweburl = match.group(0);
        applyweburl = applyweburl[1:-1];

        v("######################  ApplyWeb - browser check page  #####################")
        v("######################  from extracted applyweburl: " + applyweburl + " ########")
        c.setopt(c.URL, applyweburl);
        c.setopt(c.HTTPGET, 1);
        self.gowait(c, False, False);

        # Location of the actual browser check javascript, which we emulate below:
        #   https://www.applyweb.com/eval/browser_check/browser_check.js

        # Do the work normally done by browser_check.js:
        v("######################  ApplyWeb - redirect  #####################")
        setCookie(c, "browserCheck=true;path=/;domain=.applyweb.com;");
        # getRedirectURL()
        effurl = c.getinfo(pycurl.EFFECTIVE_URL);
        newurl = getRedirectURL(effurl);
        if newurl == None:
            raise Exception("Trouble parsing redirect url after browser check :(");
        c.setopt(c.URL, newurl);
        c.setopt(c.HTTPGET, 1);
        self.gowait(c, False, False);

        v("######################  ApplyWeb - form 1  #####################")
        # TODO: fix this random number by reading it from somewhere? 
        c.setopt(c.URL, "https://www.applyweb.com/eval/EvalGatekeeper/EvalGatekeeper?service=external/RollupReportBrowser&random=1348716484361");
        c.setopt(c.HTTPGET, 1);
        response = self.gowait(c, False, True);

        self.currentsoup = BeautifulSoup(response); # maybe use soupstrainer?
        self.selects = self.currentsoup.find_all('select');
        v(self.selects)
        print "Logged in!"

    # Submit will use the current soup to submit the form, then replace it with the 
    # new soup
    def submit(self):
        c = self.pycurler;
        
        for child in self.currentsoup.find_all('input'):
            if child.get('name') == None or child.get('value') == None:
                print "Bad <input> tag in current soup; quitting";
                print child
                raise Exception("Bad input tag in soup");
            self.formvals[child.get('name')] = child.get('value');
        fields = urllib.urlencode(self.formvals);
        
        #print "formvals: %s" % self.formvals;
        #print "Fields: %s" % fields;

        v("##### Curler.submit() ####")
        c.setopt(c.URL, "https://www.applyweb.com/eval/EvalGatekeeper/EvalGatekeeper");
        c.setopt(c.POSTFIELDS, fields);
        response = self.gowait(c, False, True);
        self.currentsoup = BeautifulSoup(response);
        return response;

    def gatherdata(self):
        print "*** Gathering Data ***"
        self.fastforward = False;

        # Create a dictionary to hold current (default) form fields
        # If we did not load a state already, load default values
        #  from the currentsoup's form
        if self.formvals == None:
            self.formvals = OrderedDict();
            for child in self.currentsoup.find_all('input'):
                self.formvals[child.get('name')] = child.get('value');
            for select in self.selects:
                self.formvals[select.get('name')] = select.option.get('value');
        else: 
            savedvals = self.formvals.copy()
            self.formvals = OrderedDict();
            for child in self.currentsoup.find_all('input'):
                self.formvals[child.get('name')] = child.get('value');
            for select in self.selects:
                self.formvals[select.get('name')] = select.option.get('value');

            v("Already loaded form values")
            self.fastforward = True;
            self.dofastforward(savedvals)

        v(self.formvals);

        # Now we're ready to make form submit requests
        self.recurse(0);

    def dofastforward(self, savedvals):
        # Get all the proper form fields to recurse down into
        for select in self.selects:
            field = select.get('name')
            self.formvals[field] = savedvals[field]
            v('fast-forwarding field %s = %s' % (field, savedvals[field]))
            self.submit();

    def recurse(self, index):
        if not self.fastforward:
            response = self.submit();
            v(("****** Recursing at depth %d #####" % index).rjust(index * 2))
        else:
            v(("****** Fast-forwarding at depth %d #####" % index).rjust(index * 2))

        formtyperound = False; # Is this the round where we pick the evaluation form type?
        # TODO: save the selects variable?
        if index >= len(self.selects):
            if self.fastforward:
                self.fastforward = False;
                v( "Found our spot!")
                # We've already saved this one (last run), so continue from there!
                return True;
            # Do stuff with the full form!
            coursenum = "%s%s" % (self.formvals['subjectSelect'], self.formvals['numberSelect'])
            term = self.formvals['termSelect'];
            return self.saveData(response, coursenum, term);
        elif index == len(self.selects) - 1:
            formtyperound = True;

        if not self.fastforward:
            # restore the form values of fields BELOW the one we're iterating on
            for i in range(index + 1, len(self.selects)):
                field = self.selects[i].get('name');
                select = self.currentsoup.find(attrs={'name' : field });
                # get the first option available
                option = select.find(name="option");
                self.formvals[field] = option.get('value');
                v( "setting %s = %s (value string %s)" % (field, option.get('value'), option.string))

        nametext = self.selects[index].get('name');
        v("Nametext: %s" % nametext)
        select = self.currentsoup.find(attrs={'name' : nametext });
        if select == None:
            print "---------------------------------- Error ----------------------------------"
            v(self.formvals)
            self.writefile(response, "pageerror.html");
            raise Exception("Error on page; couldn't find the form select tags");

        # oldval = self.formvals[nametext];
        for option in select.contents:
            # make sure we just look at actual option tags, not strings
            if not isinstance(option, Tag):
                continue;
            v( 'option: %s' % option.string)
            if option.name != 'option':
                continue;
            # ignore those with values that begin with "All"
            if re.match("All[\s]?.*", option.get('value')):
                continue;
            v( "setting %s = %s (value string %s)" % (nametext, option.get('value'), option.string))

            if self.fastforward:
                if self.formvals[nametext] != option.get('value'):
                    continue;
                # Allow the recursive call only if it is equal
            else:
                self.formvals[nametext] = option.get('value');

            # RECURSIVE STEP: 
            result = self.recurse(index+1);
            if result and formtyperound:
                v('got good results; going to next class')
                break;

        # We can't do this on a resumed data set
        #print "unsetting %s" % nametext
        #self.formvals[nametext] = oldval;
        # this return value should never be used
        return None;
        
    # Returns True if the data was good, and False if it was not
    def saveData(self, html, coursenum, term):
        # if the results not valid (not an actual class):
        bad_string = "The course you selected does not have evaluation results."
        if bad_string in html:
            v( bad_string)
            return False;

        # TODO: do stuff with self.currentsoup;
        print "%s_%s" % (coursenum, term)
        v( "Saving data")
        self.writefile(html, "%s_%s" % (coursenum, term));
        
        def isLink(element):
            if isinstance(element, Tag) and element.name == 'a' and element.string == "clicking here":
                return True;
            return False

        link = self.currentsoup.find(isLink)
        if link == None or link.get('href') == None:
            print "Failed to get written data for course %s; couldn't find link" % coursenum
        else:
            c = self.pycurler;
            effurl = getBaseURL(c.getinfo(pycurl.EFFECTIVE_URL))
            if effurl == None:
                print "Failed to get written data for course %s due to bad URL resolving" % coursenum
            else:
                effurl = "%s%s" % (effurl, link.get('href'))
                effurl = effurl.encode('ascii', 'replace')
                c.setopt(c.URL, effurl);
                c.setopt(c.HTTPGET, 1);
                advicehtml = self.gowait(c, False, True);
                v( "Saving advice data")
                self.writefile(advicehtml, "%s_%s_a" % (coursenum, term))

        # Save the good set of form values to start from if we crash
        self.saveformvals()

        return True;

parser = argparse.ArgumentParser()
parser.add_argument("maxdelay", help="the maximum number of seconds we will sleep between requests", type=int);
parser.add_argument("-v", "--verbose", help="print out lots of junk for debugging", action="store_true")
args = parser.parse_args()
Curler.VERBOSE = args.verbose
Curler.MAX_DELAY = args.maxdelay

cu = Curler();
cu.loadformvals();
cu.login();
cu.gatherdata();
