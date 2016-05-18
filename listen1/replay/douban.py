# coding=utf-8
'''
douban.fm music provider.
'''
import logging
import json
import os.path
import re
import urllib
import HTMLParser

from replay import h
from settings import MEDIA_ROOT


logger = logging.getLogger('listenone.' + __name__)


def filetype():
    return '.mp3'


def _db_h(url, v=None, auth=False):
    if auth:
        token, ck = get_douban_token_ck()
        if token is None or ck is None:
            return None
        cookie = 'dbcl2="' + token + '"; fmNlogin="y";' + \
            ' ck="' + ck + '";'
    else:
        cookie = 'ac="1460193849";'
    # http request
    extra_headers = {
        'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'douban.fm',
        'Referer': 'http://douban.fm/search',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2)' +
        ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome' +
        '/33.0.1750.152 Safari/537.36',
        'Cookie': cookie,
    }
    return h(url, v=v, extra_headers=extra_headers)


def get_douban_token_file_path():
    root_dir = MEDIA_ROOT + '/user/'
    filename = root_dir + 'douban_userinfo.json'
    return filename


def get_douban_token_ck():
    path = get_douban_token_file_path()
    if not os.path.isfile(path):
        return None, None
    with open(path, 'r') as f:
        content = f.read()
    d = json.loads(content)
    return d['token'], d['ck']


def set_douban_token_ck(token, ck):
    filename = get_douban_token_file_path()
    with open(filename, 'w') as f:
        f.write(json.dumps(dict(token=token, ck=ck)))


def remove_douban_token_ck():
    try:
        os.remove(get_douban_token_file_path())
    except:
        pass


def _gen_url_params(d):
    for k, v in d.iteritems():
        d[k] = unicode(v).encode('utf-8')
    return urllib.urlencode(d)


def _convert_song(song):
    album_title = song.get('album_title')
    if album_title is None:
        album_title = ''
    d = {
        'id': 'dbtrack_' + str(song['id']),
        'title': song['title'],
        'artist': song['artist_name'],
        'artist_id': 'dbartist_' + '0',
        'album': album_title,
        'album_id': 'dbalbum_' + '0',
        'img_url': song['cover'],
        'url': song['url'],
        'source': 'douban',
        'source_url': 'https://music.douban.com/search?q=' +
        album_title + '&sid=' + str(song['id']),
    }
    params = _gen_url_params(d)
    d['url'] = '/track_file?' + params
    return d


def _convert_song2(song):
    album_title = song.get('albumtitle')
    if album_title is None:
        album_title = ''
    d = {
        'id': 'dbtrack_' + str(song['sid']),
        'title': song['title'],
        'artist': song['singers'][0]['name'],
        'artist_id': 'dbartist_' + song['singers'][0]['id'],
        'album': album_title,
        'album_id': 'dbalbum_' + song['aid'],
        'img_url': song['picture'],
        'url': song['url'],
        'source': 'douban',
        'source_url': 'https://music.douban.com/subject/%s/' % song['aid'],
    }
    params = _gen_url_params(d)
    d['url'] = '/track_file?' + params
    return d


def _top_playlists(category=1, order='hot', offset=0, limit=60):
    action = 'https://douban.fm/j/v2/songlist/explore?type=hot&genre=1&' + \
        'limit=60&sample_cnt=5'
    data = json.loads(_db_h(action, auth=True))
    return data


# -------------standard interface part------------------


def get_captcha_token(path):
    human_url = 'https://douban.fm/j/new_captcha'
    captcha_token = h(human_url)[1:-1]
    pic_url = 'http://douban.fm/misc/captcha?size=m&id=' + captcha_token
    c = h(pic_url)
    with open(path, 'wb') as f:
        f.write(c)
    return captcha_token


def login(user, password, token, solution):
    login_url = 'https://douban.fm/j/login'
    v = dict(
        source='radio', alias=user, form_password=password,
        captcha_id=token, captcha_solution=solution, task="sync_channel_list")
    cookie = r'openExpPan=Y; flag="ok"; ac="1448675235"; bid="2dLYThA' + \
        'DnhQ";_pk_ref.100002.6447=%5B%22%22%2C%22%22%2C1448714740%2C' + \
        '%22http%3A%2F%2Fwww.douban.com%2F%22%5D; _ga=GA1.2.16347733' + \
        '49.1402330632; _pk_id.100002.6447=7d9729e0b4385d49.14023306' + \
        '33.88.1448714753.1448700119.; _pk_ses.100002.6447=*; dbcl2="' + \
        token + '"; fmNlogin="y"; ck="boPw"; _gat=1'

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) ' + \
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490' + \
        '.86 Safari/537.36'
    referer = 'http://douban.fm/'
    xwith = 'ShockwaveFlash/19.0.0.245'
    xwith = 'XMLHttpRequest'
    headers = {
        'User-Agent': user_agent,
        'Cookie': cookie,
        'Referer': referer,
        'X-Requested-With': xwith,
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2',
        'Accept-Encoding': 'gzip, deflate, sdch',
    }

    def post_handler(response, result):
        try:
            ck = json.loads(result)['user_info']['ck']
        except:
            ck = None
        cookie = response.info().getheader('Set-Cookie')
        if cookie and ck is not None:
            r = re.findall(r'dbcl2="([^"]+)"', cookie)
            if r:
                token = r[0]
                return token + '|' + ck
        else:
            return None

    return h(
        login_url, v, progress=False, extra_headers=headers,
        post_handler=post_handler, return_post=True)


def list_playlist():
    h = HTMLParser.HTMLParser()
    result = []
    for l in _top_playlists():
        d = dict(
            cover_img_url=l['cover'],
            title=h.unescape(l['title']),
            play_count=0,
            list_id='dbplaylist_' + str(l['id']),
        )
        result.append(d)
    return result


def get_playlist(playlist_id):
    url = 'http://douban.fm/j/v2/songlist/%s/?kbps=192' % playlist_id
    data = json.loads(_db_h(url, auth=True))
    info = dict(
        cover_img_url=data['cover'],
        title=data['title'],
        id='dbplaylist_' + playlist_id)
    result = []
    for song in data['songs']:
        result.append(_convert_song2(song))
    return dict(tracks=result, info=info)


def get_artist(artist_id):
    url = 'http://douban.fm/j/v2/artist/%s/' % str(artist_id)
    data = json.loads(_db_h(url, auth=True))
    info = dict(
        cover_img_url=data['avatar'],
        title=data['name_usual'],
        id='dbartist_' + artist_id)
    result = []
    for song in data['songlist']['songs']:
        result.append(_convert_song2(song))
    return dict(tracks=result, info=info)


def search_track(keyword):
    keyword = keyword.encode("utf8")
    search_url = 'http://douban.fm/j/v2/query/all?q=%s&start=0&limit=100' \
        % keyword
    data = json.loads(_db_h(search_url))
    result = []
    for song in data[1]["items"]:
        if not song['playable']:
            continue
        result.append(_convert_song(song))
    return result
