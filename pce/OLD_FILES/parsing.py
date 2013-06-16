import argparse
from bs4 import BeautifulSoup
from bs4 import Tag
from collections import OrderedDict
import itertools
import json
import os
import re
import StringIO
#import nltk
import operator

# By Candy Button, Fall 2012 Independent Work with Brian Kernighan

# Using the Natural Language Toolkit:
# Bird, Steven, Edward Loper and Ewan Klein (2009). Natural Language Processing with Python. O'Reilly Media Inc.


def v(text):
    if Parser.VERBOSE:
        print text;

def readfile(filename):
    contents = None;
    with open(filename, 'r') as f:
        contents = f.read()
    return contents

def soupfile(filename):
    html = readfile(filename)
    return BeautifulSoup(html)

def isdatafile(filename):
    # TODO
    return False

def isadvicefile(filename):
    # TODO
    return re.match(".*_a\Z", filename)

def coursenum_from_filename(filename):
    match = re.search("^.*_", filename)
    coursenum = match.group(0)[0:-1]
    return coursenum

class Parser:

    SAVE_FILE = "state_of_parser.json"
    VERBOSE = False

    def __init__(self):
        self.data = {}
        self.worddict={}

    def nextfilename(self):
        pass

    def load(self):
        try:
            f = open(Parser.SAVE_FILE, 'r')
            if f == None:
                return False
            self.data = json.load(f);
            f.close()
            v("******** LOADED DATA *******\n")
            return True
        except IOError:
            print "Failed loading data; file %s not readable" % Parser.SAVE_FILE
            return False

    def save(self):
        f = open(Parser.SAVE_FILE, 'w')
        json.dump(self.data, f)
        f.close()

    # This function requires the natural language toolkit - you must download it and 
    # uncomment the import statement (import nltk) at the top of this file
    def parse_words(self, sentences):
        words = nltk.word_tokenize(sentences)
        tags = nltk.pos_tag(words)
        
        for tag in tags:
            if tag[1] == 'JJ':
                word = tag[0];
                if self.worddict.get(word) == None:
                    self.worddict[word] = 1;
                else:
                    self.worddict[word] += 1;

    def parse_advice(self, filename):
        coursenum = coursenum_from_filename(filename);
        soup = soupfile(filename)
        tag = soup.find(name="ul")
        if tag == None:
            print "Couldn't find advice list for ", coursenum
            return False
        for item in tag.children:
            if isinstance(item, Tag) and item.name == "li":
                # Save the data in the Parser object
                # if self.data.get(filename) == None:
                #    self.data[filename] = []
                # self.data[filename].append(item.string.strip()) 

                # Or parse individual words from the string
                # self.parse_words(item.string.strip()); 

                # Print the string if in verbose mode
                v(item.string.strip())

                # INSERT YOUR CODE HERE,
                # use item.string.strip() as a single student's advice
        return True

    def parse_numbers(self, filename):
        soup = soupfile(filename)
        coursenum = coursenum_from_filename(filename);
        table = soup.find(name="table")
        # TODO: fill out the rest of the BeautifulSoup parsing to get the data here
        # INSERT YOUR CODE HERE

    def parse_dir(self):
        # "." means the current directory
        files = filter(os.path.isfile, os.listdir('.'))
        v("Advice files:")
        for file in itertools.ifilter(isadvicefile, files):
            v(file)
            self.parse_advice(file)
        v("Data files:")
        for file in itertools.ifilter(isdatafile, files):
            v(file)
            self.parse_numbers(file)
        v(self.data)

    def print_words(self):
        list = sorted(self.worddict.iteritems(), key=operator.itemgetter(1))
        for tuple in list:
            print "%s: %d" % tuple

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="print out lots of junk for debugging", action="store_true")
args = parser.parse_args()
Parser.VERBOSE = args.verbose

p = Parser();
try:
    # Loading and saving don't do anything unless you store stuff in the parser's data field, 
    # and the parsing function ignores the loaded data, so there's no use in saving/loading here.
    # p.load();

    p.parse_dir();

    # Only if you've saved words in the parser's worddict...
    # p.print_words();
    # p.save();
except Exception, e: 
    z = e
    print z
