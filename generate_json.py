from pandas import DataFrame, concat, read_pickle
from pandas.io.excel import read_excel
import sqlite3, json, re
from pandas.io import sql
from HTMLParser import HTMLParser
from numpy import isnan, isreal
import sys, cPickle,os
import random 

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

df  = read_pickle('gps_res_all.dat')

df = df.drop_duplicates('img_url')
df = df[~df.img_url.isnull()]
df.index = range(df.shape[0])

is_numeric = df.applymap(isreal)

df = df[(is_numeric.lat) & (is_numeric.lon)]

df = df[~((df.lat== 0) & (df.lon==0))]

df.lat = map(float, df.lat)
df.lon = map(float, df.lon)

print 'unique images:', len(df)

for i in df.columns:
    if(i not in ['desc', 'img_url', 'lat', 'lon', 'url']):
        df = df.drop(i, 1)  

print (df.info())

json_coords  =[]
json_props = {}
for i in df.index:
    try:  df.set_value(i, 'desc', strip_tags(df.ix[i]['desc']))
    except:   
        print i, 'could not strip tags', df.ix[i]['desc']
        df.set_value(i, 'desc', 'none')

    try:desc = df.ix[i]['desc'].encode('ascii', 'ignore').replace('&nbsp;','').strip()
    except AttributeError: desc = ''

    if(not bool(re.search('[a-z]', desc, re.IGNORECASE))):      desc = ''
    else:     re.sub(r'[\W_]+', '', desc)

    if((abs(df.ix[i]['lat']) > 85) or (abs(df.ix[i]['lon']) > 180)): continue
    else: coords = ','.join(map(str, [df.ix[i]['lon'],df.ix[i]['lat']]))

    try:
        json_coords.append(      {'type': 'Feature',
                                  "geometry": { "type": "Point", 
                                                "coordinates": [df.ix[i]['lon'],df.ix[i]['lat']]},
                                  "properties":{"desc":desc[0:300],
                                                "image": df.ix[i]['img_url'].split('//')[1],
                                                "url": df.ix[i]['url'].split('//')[1]}})
    except:
        continue

temp = open('accidental_geography/wordpress_items.js', 'w')
temp.write('wordpress_items = '+json.dumps(json_coords, separators=(',', ':'))+';') 
temp.close()

