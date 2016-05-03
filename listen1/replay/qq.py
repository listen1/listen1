# coding=utf-8
'''
qq music provider,
'''
import HTMLParser
import json
import logging
import urllib
import urllib2

from replay import h


logger = logging.getLogger('listenone.' + __name__)


def filetype():
    return '.m4a'


def _qq_h(url, v=None):
    '''
    http request
    '''
    extra_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'i.y.qq.com',
        'Referer': 'http://y.qq.com/y/static/taoge/taoge_list.html' +
        '?pgv_ref=qqmusic.y.topmenu',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2)' +
        ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome' +
        '/33.0.1750.152 Safari/537.36'
    }
    return h(url, v=v, extra_headers=extra_headers)


def _get_qqtoken():
    token_url = 'http://base.music.qq.com/fcgi-bin/fcg_musicexpress.fcg?' + \
        'json=3&guid=780782017&g_tk=938407465&loginUin=0&hostUin=0&' + \
        'format=jsonp&inCharset=GB2312&outCharset=GB2312&notice=0&' + \
        'platform=yqq&jsonpCallback=jsonCallback&needNewCode=0'
    jc = h(token_url)[len("jsonCallback("):-len(");")]
    return json.loads(jc)["key"]


def _get_image_url(qqimgid, img_type):
    if img_type == 'artist':
        category = 'mid_singer_300'
    elif img_type == 'album':
        category = 'mid_album_300'
    else:
        return None
    url = 'http://imgcache.qq.com/music/photo/%s/%s/%s/%s.jpg'
    image_url = url % (category, qqimgid[-2], qqimgid[-1], qqimgid)
    return image_url


def _gen_url_params(d):
    for k, v in d.iteritems():
        d[k] = unicode(v).encode('utf-8')
    return urllib.urlencode(d)


def _convert_song(song):
    d = {
        'id': 'qqtrack_' + str(song['songmid']),
        'title': song['songname'],
        'artist': song['singer'][0]['name'],
        'artist_id': 'qqartist_' + str(song['singer'][0]['mid']),
        'album': song['albumname'],
        'album_id': 'qqalbum_' + str(song['albummid']),
        'img_url': _get_image_url(song['albummid'], img_type='album'),
        'source': 'qq',
        'source_url': 'http://y.qq.com/#type=song&mid=' +
        str(song['songmid']) + '&tpl=yqq_song_detail',
    }
    params = _gen_url_params(d)
    d['url'] = '/track_file?' + params
    return d


# -------------standard interface part------------------


def list_playlist():
    url = 'http://i.y.qq.com/s.plcloud/fcgi-bin/fcg_get_diss_by_tag' + \
        '.fcg?categoryId=10000000&sortId=1&sin=0&ein=29&' + \
        'format=jsonp&g_tk=5381&loginUin=0&hostUin=0&' + \
        'format=jsonp&inCharset=GB2312&outCharset=utf-8' + \
        '&notice=0&platform=yqq&jsonpCallback=' + \
        'MusicJsonCallback&needNewCode=0'
    response = _qq_h(url)
    data = json.loads(response[len('MusicJsonCallback('):-len(')')])
    parser = HTMLParser.HTMLParser()
    result = []
    for l in data['data']['list']:
        d = dict(
            cover_img_url=l['imgurl'],
            title=parser.unescape(l['dissname']),
            play_count=l['listennum'],
            list_id='qqplaylist_' + str(l['dissid']),)
        result.append(d)
    return result


def get_playlist(playlist_id):
    url = 'http://i.y.qq.com/qzone-music/fcg-bin/fcg_ucc_getcdinfo_' + \
        'byids_cp.fcg?type=1&json=1&utf8=1&onlysong=0&jsonpCallback=' + \
        'jsonCallback&nosign=1&disstid=%s&g_tk=5381&loginUin=0&hostUin=0' + \
        '&format=jsonp&inCharset=GB2312&outCharset=utf-8&notice=0' + \
        '&platform=yqq&jsonpCallback=jsonCallback&needNewCode=0'
    response = _qq_h(url % playlist_id)
    data = json.loads(response[len('jsonCallback('):-len(')')])
    info = dict(
        cover_img_url=data['cdlist'][0]['logo'],
        title=data['cdlist'][0]['dissname'],
        id='qqplaylist_' + playlist_id)
    result = []
    for song in data['cdlist'][0]['songlist']:
        result.append(_convert_song(song))
    return dict(tracks=result, info=info)


def get_artist(artist_id):
    url = 'http://i.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg' + \
        '?platform=h5page&order=listen&begin=0&num=50&singermid=' + \
        '%s&g_tk=938407465&uin=0&format=jsonp&' + \
        'inCharset=utf-8&outCharset=utf-8&notice=0&platform=' + \
        'h5&needNewCode=1&from=h5&_=1459960621777&' + \
        'jsonpCallback=ssonglist1459960621772'
    response = _qq_h(url % artist_id)
    data = json.loads(response[len(' ssonglist1459960621772('):-len(')')])
    info = dict(
        cover_img_url=_get_image_url(artist_id, img_type='artist'),
        title=data['data']['singer_name'],
        id='qqartist_' + artist_id)
    result = []
    for song in data['data']['list']:
        result.append(_convert_song(song['musicData']))
    return dict(tracks=result, info=info)


def get_album(album_id):
    url = 'http://i.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg' + \
        '?platform=h5page&albummid=%s&g_tk=938407465' + \
        '&uin=0&format=jsonp&inCharset=utf-8&outCharset=utf-8' + \
        '&notice=0&platform=h5&needNewCode=1&_=1459961045571' + \
        '&jsonpCallback=asonglist1459961045566'
    response = _qq_h(url % album_id)
    data = json.loads(response[len(' asonglist1459961045566('):-len(')')])
    info = dict(
        cover_img_url=_get_image_url(album_id, img_type='album'),
        title=data['data']['name'],
        id='qqalbum_' + str(album_id))

    result = []
    for song in data['data']['list'] or []:
        result.append(_convert_song(song))
    return dict(tracks=result, info=info)


def get_url_by_id(qqsid):
    token = _get_qqtoken()
    url = 'http://cc.stream.qqmusic.qq.com/C200%s.m4a?vkey=%s' + \
        '&fromtag=0&guid=780782017'
    song_url = url % (qqsid, token)
    return song_url


def search_track(keyword):
    '''
    return matched qq music songs
    '''
    keyword = urllib2.quote(keyword.encode("utf8"))
    url = 'http://i.y.qq.com/s.music/fcgi-bin/search_for_qq_cp?' + \
        'g_tk=938407465&uin=0&format=jsonp&inCharset=utf-8' + \
        '&outCharset=utf-8&notice=0&platform=h5&needNewCode=1' + \
        '&w=%s&zhidaqu=1&catZhida=1' + \
        '&t=0&flag=1&ie=utf-8&sem=1&aggr=0&perpage=20&n=20&p=1' + \
        '&remoteplace=txt.mqq.all&_=1459991037831&jsonpCallback=jsonp4'
    response = _qq_h(url % keyword)
    data = json.loads(response[len('jsonp4('):-len(')')])

    result = []
    for song in data["data"]["song"]["list"]:
        result.append(_convert_song(song))
    return result
