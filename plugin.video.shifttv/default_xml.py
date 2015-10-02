# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys
import xbmcplugin, xbmcgui
from cookielib import CookieJar
import xml.etree.ElementTree as ET


cj = CookieJar()
    
def doLogin():
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    resp = urllib2.urlopen("http://mein.shift.tv/shift/tv/login", "login=h.arald.gutbrod%40gmail.com&password=freddy")
    login_data = resp.read()
    m = re.match(r'.*id:(\d*),.*',login_data, re.M |re.S)
    userid = m.group(1)
    return {'userid':userid, 'opener':urllib2}

def Categories():
	addDir("Favoriten", "http://mein.shift.tv/shift/tv/record/favorites/async", 20)
	
def Movies(url):
    print "starte" + url
    login = doLogin()
    userid = login['userid']    
    resp = urllib2.urlopen(url)
    fav = resp.read()
    root = ET.fromstring(fav)
    for data in root.findall("./additional/data/value/data-list/data"):
        epg = data.find("epgData")
        title = epg.get("starttime") + " - "  + epg.find("title").text
        #print epg.get("starttime")
        #print epg.find("title").text
        epgid = data.find("recording").find("epgId").text
        recid = data.find("recording").find("id").text
        #get profil id for recid (first quality)
        url = "http://mein.shift.tv/shift/tv/record/broadcasts/" + recid
        print "recUrl" + url
        resp = urllib2.urlopen(url)
        rec_xml = resp.read()
        rec_root = ET.fromstring(rec_xml)
        prof = None
        #get last profile (with the worst quality), else it wont work
        for prof in rec_root.findall("./additional/data/value/data-list/data/profileId"):
            print prof
            
        if prof is None:
            print "no downl"
            downl_url = "no"
        else:
            prof_id = prof.text
            downl_url = "http://mein.shift.tv/shift/tv/transport/download/" + epgid + '/' + prof_id + '/' +  userid
            print downl_url
            addLink(title, downl_url)
    

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
                            
    return param


def addLink(title, url):
    item = xbmcgui.ListItem(title, iconImage='DefaultVideo.png', thumbnailImage='')
    item.setInfo( type='Video', infoLabels={'Title': title} )
    url_cook = url
    #todo coocies hinzufügen
    #Cookie:JSESSIONID=A~B51D80F9E4F3F39184709B3495BB7732.stv53; hazelcast.sessionId=HZ90B1F51B0DAA49C8947732DF62DD3202; __utmt=1; __utma=233426524.1190837871.1441364940.1441376053.1441379621.4; __utmb=233426524.1.10.1441379621; __utmc=233426524; __utmz=233426524.1441364940.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _pk_ref.1.8756=%5B%22%22%2C%22%22%2C1441379627%2C%22http%3A%2F%2Fwww.shift.tv%2F%22%5D; _pk_id.1.e6c6=19993be83adf9e56.1441364945.0.1441379631..; _pk_id.1.8756=d40d2657411e6cbb.1441364945.4.1441379631.1441376080.; _pk_ses.1.8756=*
    #siehe http://kodi.wiki/view/HTTP
    cookie = ""
    for c in cj:
        if cookie == "":
            cookie = c.name + '=' + c.value
        else:
            cookie = cookie + ';' + c.name + '=' + c.value
            
    url_cook = url + '|Cookie:' + cookie
            
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url_cook, listitem=item)


def addDir(title, url, mode):
    sys_url = sys.argv[0] + '?title=' + urllib.quote_plus(title) + '&url=' + urllib.quote_plus(url) + '&mode=' + urllib.quote_plus(str(mode))

    item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage='')
    item.setInfo( type='Video', infoLabels={'Title': title} )

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)


params = get_params()
url    = None
title  = None
mode   = None

try:    title = urllib.unquote_plus(params['title'])
except: pass

try:    url = urllib.unquote_plus(params['url'])
except: pass

try:    mode = int(params['mode'])
except: pass

if mode == None:
    Categories()

elif mode == 20:
    Movies(url)

#elif mode == 30:
    #Videos(url, title)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
