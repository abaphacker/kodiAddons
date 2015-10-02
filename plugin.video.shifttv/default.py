# -*- coding: utf-8 -*-
import urllib, urllib2, re, sys
import xbmcplugin, xbmcgui
from cookielib import CookieJar
import xml.etree.ElementTree as ET
import json, time, xbmcaddon

cj = CookieJar()
addon = xbmcaddon.Addon('plugin.video.shifttv')


def doLogin():
    user = addon.getSetting('username')
    pw = addon.getSetting('password')
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    login_parm = "login=" + urllib.quote_plus(user) + "&password=" + urllib.quote_plus(pw)
    resp = urllib2.urlopen("http://mein.shift.tv/shift/tv/login", login_parm) #"login=h.arald.gutbrod%40gmail.com&password=freddy")
    login_data = resp.read()
    m = re.match(r'.*id:(\d*),.*',login_data, re.M |re.S)
    global userid 
    if m is not None:
        userid = m.group(1)
    else:
        if xbmcgui.Dialog().ok(addon.getLocalizedString(30004), addon.getLocalizedString(30005)):
            addon.openSettings()
        userid = 0
    
    print "Userid:" + str(userid)
    return {'userid':userid, 'opener':urllib2}

def Categories():
	addDir(addon.getLocalizedString(30002), "http://mein.shift.tv/shift/tv/record/favorites/async" , 20)
	addDir(addon.getLocalizedString(30003), "http://mein.shift.tv/shift/tv/record/favorites/async" , 30)
	
userid = 0

def Favs():
	url = 'http://mein.shift.tv/shift/tv/record/favorites/async'
	login = doLogin()
	if userid > 0:
		req = urllib2.Request(url, headers={"Accept" : "application/json"})
		fav = urllib2.urlopen(req ).read()
		fav_obj = json.loads(fav)
		if fav_obj['additional']['recordings'] is not None:
			listRecordings(fav_obj['additional']['recordings']['dataList'])
	
def listRecordings(list):
	for data in list:
		if 'epgData' in data:
			epg = data['epgData']
		else:
			epg = data
		
		title = time.strftime('%c',time.gmtime(epg['starttime']/1000)) + " - "  + epg['title']
		if data['recording'] is not None:
			epgid = data['recording']['epgId']
			recid = data['recording']['id']
			url = "http://mein.shift.tv/shift/tv/record/broadcasts/" + str(recid)
			print "recUrl" + url
			req = urllib2.Request(url, headers={"Accept" : "application/json"})
			rec_json = urllib2.urlopen(req).read()
			rec = json.loads(rec_json)
			
			if len(rec['additional']) == 0:
				print "no downl"
				downl_url = "no"
			else:
				prof_id = rec['additional']['data']['dataList'][0]['profileId']
				downl_url = "http://mein.shift.tv/shift/tv/transport/download/" + str(epgid) + '/' + str(prof_id) + '/' +  userid
				print downl_url
				addLink(title, downl_url)

def listSearch(url):
	#url = 'http://mein.shift.tv/shift/tv/record/favorites/async'
	print "starte" + url
	doLogin()
	if userid > 0:
		req = urllib2.Request(url, headers={"Accept" : "application/json"})
		list = urllib2.urlopen(req ).read()
		list_obj = json.loads(list)
		listRecordings(list_obj['additional']['dataList']['dataList'])

def Search():
	srch = xbmcgui.Dialog().input('Suche')
	url = 'http://mein.shift.tv/shift/tv/epg/search/entries?r=r&fieldNames=&fieldNames=&searchText=' + urllib.quote_plus(srch) 
	listSearch(url)
	
	
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
    
    cookie = ""
    for c in cj:
        if cookie == "":
            cookie = c.name + '=' + c.value
        else:
            cookie = cookie + ';' + c.name + '=' + c.value
            
    url_cook = url + '|Cookie:' + cookie + '&seekable=0'
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
    Favs()

elif mode == 30:
    Search()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
