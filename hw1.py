#!/Users/tsanzey/.brew/bin/python

# Problem 0
# chart
# 	series
# 		value
# 	graphs
# 		graph
# 			value

from fnmatch import fnmatch

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from pattern import web

from matplotlib import rcParams

def get_poll(poll_id):
	return requests.get("http://charts.realclearpolitics.com/charts/" + str(poll_id) +".xml").text

def rcp_poll_data(xml):
	dom = web.Element(xml)

	for x in xrange(0, 652):
		series = dom.by_attr(xid=str(x))
		for x in xrange(0, len(series)):
			print(series[x].content)
	return dom

poll = get_poll(1171)
rcp_poll_data(poll)
