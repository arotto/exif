from pandas import DataFrame, read_pickle
from pandas import concat
from random import shuffle
from copy import copy
from numpy import *
import pickle, socket, sys
import urllib2
try:    from bs4 import BeautifulSoup
except:    from BeautifulSoup import BeautifulSoup
import cStringIO
import PIL, datetime
import PIL.ExifTags, PIL.Image
import warnings
warnings.filterwarnings("ignore")
socket.setdefaulttimeout(2)

LANG = sys.argv[1]

url_df = read_pickle('new_lang_wordpress_urls/'+LANG+'.dat')
url_df = url_df[url_df.lang==LANG]

if('visited' not in url_df.columns): url_df['visited'] = zeros(len(url_df))

print LANG, sum(url_df.visited==0), 'unvisited sites'

gps_coords = DataFrame()
for idx in url_df.index:
    site_url = url_df.ix[idx]['url']
    lang =  url_df.ix[idx]['lang']

    if(url_df.ix[idx]['visited']==1): continue

    if('wordpress' not in site_url): continue
    site_has_images = False
    site_gps_coords = DataFrame()

    for page in range(1,11):
        if((not site_has_images) and (page == 4)): break

        url = 'http://' + site_url.strip()+ '/page/' + str(page)
        print url, lang

        try: soup = BeautifulSoup(urllib2.urlopen(url, timeout=5).read())
        except (urllib2.HTTPError, ValueError, socket.timeout, IOError ):
            url_df.set_value(idx, 'visited', 1)
            print '\tHTTP error'
            break

        for img_tag in soup.findAll('img'):
            img_url = ''
            for i in img_tag.attrs:
                if((i[0] == 'src') and (('jpg' in i[1]) or ('jpeg' in i[1]))): 
                    print '\t', i[1].split('?')[0]
                    img_url = i[1].split('?')[0] + '?w=5&h=5'

            try:
                img_url = img_tag.attrs['src'].split('?')[0] + '?w=1h=1'
            except: pass

            if('wordpress' not in img_url): continue

            try:
                file = cStringIO.StringIO(urllib2.urlopen(img_url, timeout=5).read())
                img = PIL.Image.open(file)
            except (urllib2.HTTPError, ValueError, socket.timeout, IOError ):
                continue

            try:
                exif = {
                    PIL.ExifTags.TAGS[k]: v
                    for k, v in img._getexif().items()
                    if k in PIL.ExifTags.TAGS
                    }
            except (AttributeError,IndexError, IOError,SyntaxError):
                continue

            if( sum(['gps' in i.lower() for i in exif.keys()]) > 0):
                print '\tGPS info found: '
                try:
                    lat = (exif['GPSInfo'][2][0][0]/float(exif['GPSInfo'][2][0][1]) + exif['GPSInfo'][2][1][0]/float(exif['GPSInfo'][2][1][1])/60 +  exif['GPSInfo'][2][2][0]/float(exif['GPSInfo'][2][2][1])/3600.) * {True: -1, False: 1}[exif['GPSInfo'][1] == 'S']
                    lon = (exif['GPSInfo'][4][0][0]/float(exif['GPSInfo'][4][0][1]) + exif['GPSInfo'][4][1][0]/float(exif['GPSInfo'][4][1][1])/60 +  exif['GPSInfo'][4][2][0]/float(exif['GPSInfo'][4][2][1])/3600.) * {True: -1, False: 1}[exif['GPSInfo'][3] == 'W']
                    site_has_images = True
                except (KeyError, ZeroDivisionError, IndexError, TypeError):
                    print '\t bad GPS format'
                    break

                print '\t\t', lat, lon
                
                if(img_tag.parent.parent.contents.__class__ == list):
                    txt = ''
                    for i in img_tag.parent.parent.text:
                        try:  txt += ( str(i).encode('ascii', 'ignore'))
                        except: pass
                else:
                    txt = img_tag.parent.parent.text.encode('ascii', 'ignore')

                if(txt.strip() == ''): txt = 'none'

                site_gps_coords = site_gps_coords.append( {'desc':txt, 'url':url, 'img_url':img_url.split('?')[0],
                                                 'lat':lat, 'lon':lon}, ignore_index=True )

    url_df.set_value(idx, 'visited', 1)
    
    if(site_has_images): 
        site_gps_coords.to_csv('output/gps_res_'+LANG+'.csv', mode='a', header=False)
        url_df.to_pickle('new_lang_wordpress_urls/'+LANG+'.dat')
