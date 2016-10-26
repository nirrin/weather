#!/usr/bin/env python

import datetime
import urllib
from bs4 import BeautifulSoup

def hmdmy():
	now = datetime.datetime.now()
	return now.hour, now.minute, now.day, now.month, now.year

def parse(url):
	r = urllib.urlopen(url).read()
	print r
	soup = BeautifulSoup(r, "lxml")	
	print soup.prettify()



if __name__ == "__main__":
	print parse("http://www.google.com")