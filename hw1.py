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

import re

def _strip(s):
    """This function removes non-letter characters from a word
    
    for example _strip('Hi there!') == 'Hi there'
    """
    return re.sub(r'[\W_]+', '', s)

def plot_colors(xml):
    """
    Given an XML document like the link above, returns a python dictionary
    that maps a graph title to a graph color.
    
    Both the title and color are parsed from attributes of the <graph> tag:
    <graph title="the title", color="#ff0000"> -> {'the title': '#ff0000'}
    
    These colors are in "hex string" format. This page explains them:
    http://coding.smashingmagazine.com/2012/10/04/the-code-side-of-color/
    
    Example
    -------
    >>> plot_colors(get_poll_xml(1044))
    {u'Approve': u'#000000', u'Disapprove': u'#FF0000'}
    """
    dom = web.Element(xml)
    result = {}
    for graph in dom.by_tag('graph'):
        title = _strip(graph.attributes['title'])
        result[title] = graph.attributes['color']
    return result
#these colors come from colorbrewer2.org. Each is an RGB triplet
dark2_colors = [(0.10588235294117647, 0.6196078431372549, 0.4666666666666667),
                (0.8509803921568627, 0.37254901960784315, 0.00784313725490196),
                (0.4588235294117647, 0.4392156862745098, 0.7019607843137254),
                (0.9058823529411765, 0.1607843137254902, 0.5411764705882353),
                (0.4, 0.6509803921568628, 0.11764705882352941),
                (0.9019607843137255, 0.6705882352941176, 0.00784313725490196),
                (0.6509803921568628, 0.4627450980392157, 0.11372549019607843),
                (0.4, 0.4, 0.4)]

rcParams['figure.figsize'] = (10, 6)
rcParams['figure.dpi'] = 150
rcParams['axes.color_cycle'] = dark2_colors
rcParams['lines.linewidth'] = 2
rcParams['axes.grid'] = True
rcParams['axes.facecolor'] = '#eeeeee'
rcParams['font.size'] = 14
rcParams['patch.edgecolor'] = 'none'

def poll_plot(poll_id):
    """
    Make a plot of an RCP Poll over time
    
    Parameters
    ----------
    poll_id : int
        An RCP poll identifier
    """

    # hey, you wrote two of these functions. Thanks for that!
    xml = get_poll_xml(poll_id)
    data = rcp_poll_data(xml)
    colors = plot_colors(xml)

    #remove characters like apostrophes
    data = data.rename(columns = {c: _strip(c) for c in data.columns})

    #normalize poll numbers so they add to 100%    
    norm = data[colors.keys()].sum(axis=1) / 100    
    for c in colors.keys():
        data[c] /= norm
    
    for label, color in colors.items():
        plt.plot(data.date, data[label], color=color, label=label)        
        
    plt.xticks(rotation=70)
    plt.legend(loc='best')
    plt.xlabel("Date")
    plt.ylabel("Normalized Poll Percentage")

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
	dom = web.Element(html)
	result = []

	for ahref in dom.by_tag('a'):
		name = ahref.attributes.get('href', '')
		reg1 = 'http://www.realclearpolitics.com/epolls/????/governor/??/*-*.html'
		reg2 = '/epolls/????/governor/??/*-*.html'
		if fnmatch.fnmatch(name, reg1):
			result.append(name)
		elif fnmatch.fnmatch(name, reg2):
			result.append("http://www.realclearpolitics.com" + name)
	return result

def race_result(url):
	dom = web.Element(requests.get(url).text)
	result = {}
	total = 0

	gov_names = []
	election_results = []
	th = dom.by_class('data')[0].by_tag('th')
	for n in range(3, len(th) - 1):
		gov_names.append(th[n].content.split()[0])
	td = dom.by_class('final')[0].by_tag('td')
	for r in range(3, len(td) - 1):
		total += float(td[r].content)
	i = 0
	for x in gov_names:
		result[str(x)] = float(td[3 + i].content) / total * 100 #Do not forget to normalize
		i += 1
	return result

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
	print(result)
	# for r in result:
	# 	plt.axhline(result[r], color=colors[_strip(r)], alpha=0.6, ls='--')

def all_error_data():
	page = requests.get('http://www.realclearpolitics.com/epolls/2010/governor/2010_elections_governor_map.html').text.encode('ascii', 'ignore')
	frames = []
	for err in find_governor_races(page):
		frames.append(error_data(err))
		df = pd.concat(frames, ignore_index=True)
		return df

# poll_plot(1044)
# plt.title("Obama Job Approval")
# plt.show()

