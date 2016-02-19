from xbmcswift2 import Plugin
import os
import xbmc
import sys
from BeautifulSoup import BeautifulSoup as BS
import requests
import re
plugin = Plugin()

lib = 'special://home' + '/addons/' + plugin._addon_id
lib = xbmc.translatePath(lib)
print lib
lib = os.path.join( lib, 'resources', 'lib')
print lib
sys.path.append(lib)

sys.path.append (xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'lib' ) ))
 

@plugin.route('/')
def index():
    items = [{
        'label': 'Viperial',
        'path': plugin.url_for('viperial')},{
		'label': 'AlbumKings',
        'path': plugin.url_for('albumkings')
        
    },{
		'label': 'MonsterMixtapes',
		'path':plugin.url_for('monstermixtapes')
		}]
	
    return items
@plugin.route('/viperial/')	
def viperial():
	items = [{
				'label': 'Search Tracks...',
				'path': plugin.url_for('search',src='viperial')
				},{
				'label': 'Latest Hot Tracks',
				'path': plugin.url_for('vip_hot',src='viperial',hot = 1, page = '1')
				}
			]
	return items
@plugin.route('/albumkings/')	
def albumkings():
	items = [{
				'label': 'Search Albums...',
				'path': plugin.url_for('search',src='albumkings')
				},{
				'label': 'On Display',
				'path': plugin.url_for('display',src='albumkings',display = 'display')
				},{
				'label': 'Top Albums',
				'path': plugin.url_for('display',src='albumkings',display = 'top')
				}
				
			]
	return items
	
@plugin.route('/monstermixtapes/')	
def monstermixtapes():
	items = [{
				'label': 'Search Mixtapes...',
				'path': plugin.url_for('search',src='mixtapes')
				},{
				'label': 'Featured',
				'path': plugin.url_for('display',src='mixtapes',display = 'display')
				}
				,{
				'label': 'Most Downloaded',
				'path': plugin.url_for('display',src='mixtapes',display = 'top')
				}
			]
	return items	
@plugin.route('/search/<src>/<display>/', name = 'display')
@plugin.route('/search/<src>/<search_term>/<page>/', name = 'search_one')
@plugin.route('/search/<src>/<hot>/<page>/', name = 'vip_hot')
@plugin.route('/search/<src>/')
def search(src = '',search_term = '',page = '1',hot = 0, display = ''):
	items = []
	
	if len(search_term) == 0 and hot == 0 and display == '':
		search_term = plugin.keyboard(heading = 'Enter Search Term')
	plugin.log.info('HOT %s' % hot)
	if src == 'viperial':
		url = 'http://www.viperial.org/search/tracks?q=%s' % search_term
		if str(hot) == '1':
			url = 'http://www.viperial.org/tracks/imaged/%s' % page
		r = requests.get(url)
		soup = BS(r.text)
		for track in soup.findAll('a',	attrs = {'href':re.compile('tracks/view')}):
			isHot = 0
			plugin.log.info('TRACK %s' % str(track))
			if str(hot) == '1':
				try: 
					if track['class'] == 'artist' or track['class'] == 'name': continue
				except: pass
				try:
					if track.string: continue
				except:pass
			name = ''
			link = track['href']
			info = track_info(src='viperial',url = link)
			if str(hot) == '1': 
				hotstring = str(track)
			else: hotstring = str(track.parent)
			if 'hot1' in hotstring:
				name+='[COLOR red][HOT] [/COLOR]'
				isHot = 1
			if 'hot2' in hotstring:
				name+= '[COLOR yellow][HOT] [/COLOR]'
				isHot = 1
			name+= info['artist'] + ' - ' + info['track']
			# plugin.log.info('NAME %s' % name)
			# if hot == 1: name = track.string
			plugin.log.info('URL %s' % link)
			plugin.log.info('ISHOT %s' % isHot)
			labs = {'Artist':info['artist'],'Title':info['track']}
			item= {
				'label': name,
				'path': info['url'],
				'thumbnail': info['img'],
				'info_type': 'music',
				'info' : labs,
				'is_playable': True
				}
			if (str(hot) == '1' and isHot == 1) or str(hot) == '0': items.append(item)
	if src == 'albumkings' or src == 'mixtapes':
		if src == 'albumkings':
			if display: url = 'http://www.albumkings.in/'
			else: url = 'http://www.albumkings.in/search?q=%s&page=%s' % (search_term,page)
		if src == 'mixtapes':
			if display: url = 'http://www.monstermixtapes.net/'
			else: url = 'http://www.monstermixtapes.net/search?q=%s&page=%s' % (search_term,page)
		r = requests.get(url)
		soup = BS(r.text)
		if display == 'display':
			records = soup.find(attrs = {'class':'section colored gray three-items'}).findAll(attrs = {'class' : 'record'})
		elif display == 'top' and src == 'mixtapes':
			records = soup.findAll(attrs = {'class':'widget'})[1].findAll(attrs = {'class':'row'})
			plugin.log.info(records)
		elif display == 'top' and src == 'albumkings':
			records = soup.findAll(attrs = {'class':'widget'})[1].findAll(attrs = {'class':'row'})
		else: records = soup.findAll(attrs = {'class' : 'record'})
		for album in records:
			item = {
				'label': album.a.img['alt'],
				'thumbnail': album.a.img['src'],
				'path' : plugin.url_for('albums', url = album.a['href'], img = album.a.img['src'])
				}
			items.append(item)
	if str(hot) == '0':
		items.append({
				'label': 'Next Page >>',
				'path': plugin.url_for('search_one',src = src, search_term = search_term, page = str(int(page)+1))})
	else: 
		items.append({
				'label': 'Next Page >>',
				'path': plugin.url_for('vip_hot',src = src,hot = 1, page = str(int(page)+1))})
	return items



def track_info(url = '', src = ''):
	if src == 'viperial':
		base_url = 'http://www.viperial.org/'
	soup = BS(requests.get(base_url + url).text)
	file = soup.find(attrs = {'flashvars': re.compile('file=')})['flashvars']
	stream = file.split('file=')[1]
	img = soup.img['src']
	title = soup.find(attrs = {'class':'title'})
	artist = title.text.split(' -')[0]
	track = title.text.split(' -')[1]
	img_url = base_url+img
	plugin.log.info('IMG %s' % img_url)
	return {'url':stream, 'img':img_url, 'artist' :artist, 'track': track}
@plugin.route('/albums/<url>/<img>/')	
def albums(url = '',img = ''):
	r = requests.get(url)
	soup = BS(r.text)
	items = []
	for track in soup.findAll(attrs = {'data-file':re.compile('')}):
		aa = soup.find(attrs={'class':'col-sm-7'}).h1.text
		labs = {'album':aa.split(' -')[1],'artist':aa.split(' -')[0],'title':track.parent.span.string}
		item = {
			'label': track.parent.span.string,
			'path': track['data-file'],
			'thumbnail':img,
			'info_type': 'music',
			'info' : labs,
			'is_playable': True
			}
		items.append(item)
	return items

if __name__ == '__main__':
    plugin.run()
