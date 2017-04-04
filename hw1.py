#!/Users/tsanzey/.brew/bin/python

# Problem 0
# chart
# 	series
# 		value
# 	graphs
# 		graph
# 			value

import fnmatch

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from pattern import web

from matplotlib import rcParams

def get_poll_xml(poll_id):
	return requests.get("http://charts.realclearpolitics.com/charts/" + str(poll_id) +".xml").text

def rcp_poll_data(xml): 
	dom = web.Element(xml)
	result = {}

	dates = dom.by_tag('series')[0]    
	dates = {n.attributes['xid']: str(n.content) for n in dates.by_tag('value')}

	keys = dates.keys()

	result['date'] = pd.to_datetime([dates[k] for k in keys])

	for graph in dom.by_tag('graph'):
		name = graph.attributes['title']
		data = {n.attributes['xid']: float(n.content) 
		if n.content else np.nan for n in graph.by_tag('value')}
		result[name] = [data[k] for k in keys]
	result = pd.DataFrame(result)    
	result = result.sort_values(by=['date'])
	return result

def find_governor_races(html):
	page = requests.get(html).text
	dom = web.Element(page)
	result = []

	regex = fnmatch.translate('*http://www.realclearpolitics.com/epolls/*')
	for ahref in dom.by_tag('a'):
		name = ahref.attributes.get('href', '')
		if fnmatch.fnmatch(name, 'http://www.realclearpolitics.com/epolls/[0-9][0-9][0-9][0-9]/governor/[a-zA-Z][a-zA-Z]/*[0-9][0-9][0-9][0-9].html'):
			result.append(name)
	return result

def race_result(url):
	dom = web.Element(requests.get(url).text)
	result = {}

	gov_names = []
	election_results = []
	names = dom.by_class('candidate layout0')
	for n in names:
		alt = web.Element(n)
		alt = alt.by_tag('img')
		gov_names.append(alt[0].attributes['alt'].split()[1])
	final = dom.by_class('final')[0]
	final = web.Element(final)
	td = final.by_tag('td')
	total = float(td[3].content + td[4].content) / 100
	result[gov_names[0]] = td[3].content
	result[gov_names[1]] = td[4].content
	return result

def race_result2(url):
	
	dom = web.Element(requests.get(url).text)
	
	table = dom.by_tag('div#polling-data-rcp')[0]
	result_data = table.by_tag('tr.final')[0]
	td = result_data.by_tag('td')

	results = [float(t.content) for t in td[3:-1]]
	tot = sum(results) / 100
	
	#get table headers
	headers = table.by_tag('th')
	labels = [str(t.content).split('(')[0].strip() for t in headers[3:-1]]
	print("labels", labels)
	print("results", results)
	for l, r in zip(labels, results):
		print(l, r / tot)
	return {l:r / tot for l, r in zip(labels, results)}

def id_from_url(url):
	"""Given a URL, look up the RCP identifier number"""
	return url.split('-')[-1].split('.html')[0]

def plot_race(url):
	"""Make a plot summarizing a senate race
	
	Overplots the actual race results as dashed horizontal lines
	"""
	#hey, thanks again for these functions!
	id = id_from_url(url)
	xml = get_poll_xml(id)	
	
	#really, you shouldn't have
	result = race_result(url)
	# print(result)	
	for r in result:
		plt.axhline(result[r], color=colors[_strip(r)], alpha=0.6, ls='--')

# find_governor_races("http://www.realclearpolitics.com/epolls/2010/governor/2010_elections_governor_map.html")
print(race_result("http://www.realclearpolitics.com/epolls/2010/governor/ca/california_governor_whitman_vs_brown-1113.html"))
print(race_result2("http://www.realclearpolitics.com/epolls/2010/governor/ca/california_governor_whitman_vs_brown-1113.html"))
# page = requests.get('http://www.realclearpolitics.com/epolls/2010/governor/2010_elections_governor_map.html').text.encode('ascii', 'ignore')

# for race in find_governor_races(page):
# 	plot_race(race)