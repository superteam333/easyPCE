import os
import re
import sys
sys.path.append('/users/matt/develop/easypce/')
from myapp import settings
from django.core.management import setup_environ
setup_environ(settings)
from models import *

advice = Advice.objects.all()
word_count = []
for a in advice:
	words = a.text.split()
	for w in words:
		if len(word_count) == 0:
			word_count.append((w, 0))
		for i in range(len(word_count)):
			if (word_count[i][0].lower() == w.lower()):
				word_count[i] = (word_count[i][0], word_count[i][1]+1)
			else:
				word_count.append((w, 0))

for wc in word_count:
	print wc[0] + ": " + wc[1]