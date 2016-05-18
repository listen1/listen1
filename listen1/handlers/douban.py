# coding=utf8
import glob
import json
import logging
import os
import os.path
import urllib
import uuid

import tornado.httpclient

from handlers.base import BaseHandler
from settings import MEDIA_ROOT
from replay.douban import get_captcha_token, \
    login, remove_douban_token_ck, get_douban_token_ck, set_douban_token_ck
from models.playlist import PlaylistManager


logger = logging.getLogger('listenone.' + __name__)


class FetchManager():
    def __init__(self, token=None, ck=None):
        self.status = 'stop'
        self.sid_list_count = 0
        self.sid_list = []
        self.result = []

        self.client = tornado.httpclient.AsyncHTTPClient()
        cookie = r'flag="ok"; ac="1458457738"; bid="2dLYThADnhQ"; _pk_ref' + \
            '.100002.6447=%5B%22%22%2C%22%22%2C1458457740%2C%22https' + \
            '%3A%2F%2Fmusic.douban.com%2F%22%5D; _pk_id.100002.6447=390c6c' + \
            '20836ad808.1456577744.3.1458457764.1458264315.; dbcl2="' + \
            token + '"; fmNlogin="y"; ck="' + ck + \
            '"; openExpPan=Y; _ga=GA1.2.1945208436.1456577744'

        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) ' + \
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 ' + \
            'Safari/537.36'
        referer = 'http://douban.fm/'
        xwith = 'ShockwaveFlash/19.0.0.245'
        self.headers = {
            'User-Agent': user_agent,
            'Cookie': cookie,
            'Referer': referer,
            'X-Requested-With': xwith,
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2',
            'Accept-Encoding': 'gzip, deflate, sdch',
        }
        self.step = 20

        self.token = token
        self.ck = ck

    def start(self):
        if self.status == 'finished':
            return
        self.status = 'progress'

        url = 'http://douban.fm/j/v2/redheart/basic'
        request = tornado.httpclient.HTTPRequest(url=url, headers=self.headers)
        self.client.fetch(request, self._on_download)

    def _on_download(self, response):
        # get red heart sids
        result = json.loads(response.body)
        self.sid_list = [i['sid'] for i in result['songs']]
        self.sid_list_count = len(self.sid_list)
        self._on_download2()

    def _on_download2(self, response=None):
        if response is not None:
            for d in json.loads(response.body):
                real_url = d['url']
                url = '/track_file?' + urllib.urlencode(dict(
                    url=real_url,
                    artist=d['singers'][0]['name'].encode("utf8"),
                    album=d['albumtitle'].encode("utf8"),
                    title=d['title'].encode("utf8"),
                    id=d['sid'],
                    source='douban'))
                track = {
                    'id': 'dbtrack_' + str(d['sid']),
                    'title': d['title'],
                    'artist': d['singers'][0]['name'],
                    'artist_id': 'dbartist_' + d['singers'][0]['id'],
                    'album': d['albumtitle'],
                    'album_id': 'dbalbum_' + d['aid'],
                    'img_url': d['picture'],
                    'url': url,
                    'source': 'douban',
                    'source_url': 'https://music.douban.com/subject/%s/' %
                    d['aid'],
                }
                self.result.append(track)

        url = 'http://douban.fm/j/v2/redheart/songs'
        handle_list = self.sid_list[:self.step]

        if handle_list == []:
            self.status = 'finished'
            # create playlist for douban red heart songs
            PlaylistManager.shared_instance()\
                .create_playlist(u'豆瓣红心', tracks=self.result)
            return

        self.sid_list = self.sid_list[self.step:]
        sids = '|'.join(handle_list)
        v = dict(sids=sids, kbps="192", ck=self.ck)
        request = tornado.httpclient.HTTPRequest(
            url=url, method='POST',
            body=urllib.urlencode(v), headers=self.headers)
        self.client.fetch(request, self._on_download2)
        logger.debug('fetch url for douban red heart:' + url)

    def get_status(self):
        # status: stop, progress, finish
        if self.sid_list_count == 0:
            progress = 0
        else:
            finished = self.sid_list_count - len(self.sid_list)
            progress = int(finished * 100 / self.sid_list_count)
        return dict(status=self.status, progress=progress, result=self.result)

manager = None


def _get_captcha():
    # get valid code from douban server
    # save it to temp folder
    filename = str(uuid.uuid4()) + '.jpg'
    path = MEDIA_ROOT + '/temp/' + filename
    token = get_captcha_token(path)
    return dict(path='/static/temp/' + filename, token=token)


def _clear_temp_folder():
    path = MEDIA_ROOT + '/temp/'
    files = glob.glob(path + '*')
    for f in files:
        os.remove(f)


class ValidCodeHandler(BaseHandler):
    def get(self):
        token, ck = get_douban_token_ck()
        if token is not None and ck is not None:
            result = dict(isLogin='1')
        else:
            result = dict(isLogin='0', captcha=_get_captcha())
        self.write(result)


class DBLoginHandler(BaseHandler):
    @classmethod
    def get_store_filename(cls):
        root_dir = MEDIA_ROOT + '/user/'
        filename = root_dir + 'douban_userinfo.json'
        return filename

    def post(self):
        user = self.get_argument('user')
        password = self.get_argument('password')
        token = self.get_argument('token')
        solution = self.get_argument('solution')
        token = login(user, password, token, solution)
        if token == 'deleted' or token is None:
            result = _get_captcha()
            result['success'] = '0'
        else:
            l = token.split('|')
            realtoken, ck = l[0], l[1]
            user_info = dict(token=realtoken, ck=ck)
            set_douban_token_ck(token=realtoken, ck=ck)
            result = dict(token=token, success='1', user=user_info)
            _clear_temp_folder()
        self.write(dict(result=result))


class DBLogoutHandler(BaseHandler):
    def get(self):
        remove_douban_token_ck()
        self.write(dict(result=dict(success='1')))


class DBFavoriteHandler(BaseHandler):
    def post(self):
        global manager
        # favorite task fetch command service
        command = self.get_argument('command')
        if command == 'start':
            token, ck = get_douban_token_ck()
            manager = FetchManager(token, ck)
            manager.start()
            status = manager.get_status()
            self.write(dict(result=status))
        elif command == 'status':
            if manager is None:
                self.write(dict(result=dict(
                    status='notstarted', progress=0, result=[])))
            else:
                status = manager.get_status()
                self.write(dict(result=status))
