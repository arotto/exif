from pandas import DataFrame
import cPickle, pickle, socket
import urllib2
try:    from bs4 import BeautifulSoup
except:    from BeautifulSoup import BeautifulSoup
import cStringIO
import PIL, datetime
import PIL.ExifTags
from fake_useragent import UserAgent
from urllib import FancyURLopener
from collections import Counter
from random import shuffle
import string, codecs
import HTMLParser, re
import warnings
from py_bing_search import PyBingWebSearch

warnings.filterwarnings("ignore")

LANG = 'es' #for example, grab the spanish corpus

my_key = 'fake_key'  #THIS IS WHERE YOUR BING SEARCH API KEY GOES


'''
regex = re.compile('[^a-zA-Z ]')
words = map(lambda x:' '.join(x.split(' ')[0:2]).strip(), codecs.open('corpora_etc/'+LANG + '-wordbigrams.txt', encoding='utf-8').readlines())
words = map( lambda x:regex.sub('', x), words)
words = map(lambda x:x.strip(), filter(lambda x: not x.isspace(), words))
words = filter(lambda x: len(x)> 1, words)

new_words = []
for word in words:
    if( (len(word.split(' ')) > 1) and (len(map(lambda x:len(x)>1,   word.split(' '))) == sum(map(lambda x:len(x)>1,   word.split(' '))))):
        new_words.append(word)

words = new_words
'''

words = map(lambda x:x.split(' ')[0], codecs.open('corpora/'+LANG + '-words.txt', encoding='utf-8').readlines())

print 'using:', len(words), 'words'


urls = set()
print 'language', LANG
for word in words[0:500]:
    print word.split(',')[0]

    try:
        word = unicode(word)
    except UnicodeDecodeError:
        print '...skipping'
        continue
    
    query_string = '"' + word + '" site:wordpress.com'

    bing = BingSearchAPI(my_key)

    for i in range(0, 50): 
        params = { '$format': 'json',              '$top': 50,              '$skip': i*50}

        try:
            x = bing.search('web',query_string,params).json()['d']['results'][0]

        except ValueError:
            print 'error...:', bing.search('web',query_string,params)
            continue

        print i, len(x['Web'])
        for res in x['Web']:
            url = res['Url'].encode('ascii', 'ignore')

            if('files' in url): continue
            try:
                if('https' in url):
                    urls.add(url.split('https://')[1].split('/')[0])
                elif('http' in url):
                    urls.add(url.split('http://')[1].split('/')[0])            
            except:
                print url

df = DataFrame()
for url in list(urls):
    df = df.append( {'lang':LANG, 'url':url}, ignore_index=True)

df.to_pickle('new_lang_wordpress_urls/'+LANG+'.dat')

