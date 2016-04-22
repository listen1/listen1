# coding=utf-8
'''
netease music provider.
'''
import base64
import hashlib
import json
import logging
import os.path
import urllib
import urllib2

import pyaes

from replay import h


logger = logging.getLogger('listenone.' + __name__)


def filetype():
    return '.mp3'


# 歌曲加密算法, 基于https://github.com/yanunon/NeteaseCloudMusic脚本实现
def _encrypted_id(id):
    magic = bytearray('3go8&$8*3*3h0k(2)2')
    song_id = bytearray(id)
    magic_len = len(magic)
    for i in xrange(len(song_id)):
        song_id[i] = song_id[i] ^ magic[i % magic_len]
    m = hashlib.md5(song_id)
    result = m.digest().encode('base64')[:-1]
    result = result.replace('/', '_')
    result = result.replace('+', '-')
    return result


modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b72' + \
    '5152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbd' + \
    'a92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe48' + \
    '75d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
nonce = '0CoJUm6Qyw8W8jud'
pubKey = '010001'


def _create_secret_key(size):
    randlist = map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))
    return (''.join(randlist))[0:16]


def _aes_encrypt(text, sec_key):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    aes = pyaes.AESModeOfOperationCBC(sec_key, iv='0102030405060708')
    ciphertext = ''
    while text != '':
        ciphertext += aes.encrypt(text[:16])
        text = text[16:]
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext


def _rsa_encrypt(text, pub_key, modulus):
    text = text[::-1]
    rs = int(text.encode('hex'), 16) ** int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)


def _encrypted_request(text):
    text = json.dumps(text)
    sec_key = _create_secret_key(16)
    enc_text = _aes_encrypt(_aes_encrypt(text, nonce), sec_key)
    enc_sec_key = _rsa_encrypt(sec_key, pubKey, modulus)
    data = {
        'params': enc_text,
        'encSecKey': enc_sec_key
    }
    return data


# 参考 https://github.com/darknessomi/musicbox
# 歌单（网友精选碟） hot||new http://music.163.com/#/discover/playlist/
def _top_playlists(category=u'全部', order='hot', offset=0, limit=60):
    category = urllib2.quote(category.encode("utf8"))
    action = 'http://music.163.com/api/playlist/list?cat=' + category + \
        '&order=' + order + '&offset=' + str(offset) + \
        '&total=' + ('true' if offset else 'false') + '&limit=' + str(limit)
    data = json.loads(_ne_h(action))
    return data['playlists']


def _ne_h(url, v=None):
    # http request
    extra_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'music.163.com',
        'Referer': 'http://music.163.com/search/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2)' +
        ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome' +
        '/33.0.1750.152 Safari/537.36'
    }
    return h(url, v=v, extra_headers=extra_headers)


def _gen_url_params(d):
    for k, v in d.iteritems():
        d[k] = unicode(v).encode('utf-8')
    return urllib.urlencode(d)


def _convert_song(song):
    d = {
        'id': 'netrack_' + str(song['id']),
        'title': song['name'],
        'artist': song['artists'][0]['name'],
        'artist_id': 'neartist_' + str(song['artists'][0]['id']),
        'album': song['album']['name'],
        'album_id': 'nealbum_' + str(song['album']['id']),
        'source': 'netease',
        'source_url': 'http://music.163.com/#/song?id=' + str(song['id']),
    }
    if 'picUrl' in song['album']:
        d['img_url'] = song['album']['picUrl']
    else:
        d['img_url'] = ''
    params = _gen_url_params(d)
    d['url'] = '/track_file?' + params
    return d

# -------------standard interface part------------------


# https://github.com/darknessomi/musicbox/wiki/%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90%E6%96%B0%E7%89%88WebAPI%E5%88%86%E6%9E%90%E3%80%82
def get_url_by_id(song_id):
    csrf = ''
    d = {
        "ids": [song_id],
        "br": 12800,
        "csrf_token": csrf
    }
    url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token='
    request = _encrypted_request(d)
    response = json.loads(_ne_h(url, request))
    return response['data'][0]['url']


def list_playlist():
    result = []
    for l in _top_playlists():
        d = dict(
            cover_img_url=l['coverImgUrl'],
            title=l['name'],
            play_count=l['playCount'],
            list_id='neplaylist_' + str(l['id']),)
        result.append(d)
    return result


def get_playlist(playlist_id):
    url = 'http://music.163.com/api/playlist/detail?id=' + playlist_id
    data = json.loads(_ne_h(url))
    info = dict(
        cover_img_url=data['result']['coverImgUrl'],
        title=data['result']['name'],
        id='neplaylist_' + playlist_id)
    result = []
    for song in data['result']['tracks']:
        if song['status'] == -1:
            continue
        result.append(_convert_song(song))
    return dict(tracks=result, info=info)


def get_artist(artist_id):
    url = 'http://music.163.com/api/artist/' + str(artist_id)
    data = json.loads(_ne_h(url))
    info = dict(
        cover_img_url=data['artist']['picUrl'],
        title=data['artist']['name'],
        id='neartist_' + artist_id)
    result = []
    for song in data['hotSongs']:
        if song['status'] == -1:
            continue
        result.append(_convert_song(song))
    return dict(tracks=result, info=info)


def get_artist_albums(artist_id):
    url = 'http://music.163.com/api/artist/albums/' + str(artist_id) + \
        '?offset=0&limit=50'
    try:
        data = json.loads(_ne_h(url))
        return data['hotAlbums']
    except:
        return []


def get_album(album_id):
    url = 'http://music.163.com/api/album/%s/' % album_id
    data = json.loads(_ne_h(url))
    info = dict(
        cover_img_url=data['album']['picUrl'],
        title=data['album']['name'],
        id='nealbum_' + str(album_id))

    result = []
    for song in data['album']['songs']:
        if song['status'] == -1:
            continue
        result.append(_convert_song(song))
    return dict(tracks=result, info=info)


def search_track(keyword):
    # return matched qq music songs
    keyword = keyword.encode("utf8")
    search_url = 'http://music.163.com/api/search/get'
    stype = 1
    offset = 0
    total = 'true'
    data = {
        's': keyword,
        'type': stype,
        'offset': offset,
        'total': total,
        'limit': 60
    }
    jc = _ne_h(search_url, data)
    result = []
    for song in json.loads(jc)["result"]["songs"]:
        if song['status'] == -1:
            continue
        result.append(_convert_song(song))
    return result
