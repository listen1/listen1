# coding=utf8
import logging

from handlers.base import BaseHandler
from replay import get_provider

logger = logging.getLogger('listenone.' + __name__)


class ArtistHandler(BaseHandler):
    def get(self):
        artist_id = self.get_argument('artist_id', '')
        provider = get_provider(artist_id)
        provider_name, artist_id = \
            artist_id.split('_')[0], artist_id.split('_')[1]

        if provider_name == 'dbartist':
            if artist_id == '0':
                result = dict(status='0', reason='豆瓣暂不提供艺术家信息')
                self.write(result)
                return

        artist = provider.get_artist(artist_id)
        result = dict(
            status='1',
            tracks=artist['tracks'],
            info=artist['info'],
            is_mine='0')
        self.write(result)


class AlbumHandler(BaseHandler):
    def get(self):
        album_id = self.get_argument('album_id', '')
        provider = get_provider(album_id)

        provider_name, album_id = \
            album_id.split('_')[0], album_id.split('_')[1]

        if provider_name == 'dbalbum':
            result = dict(status='0', reason='豆瓣暂不提供专辑信息')
            self.write(result)
            return

        album = provider.get_album(album_id)
        result = dict(
            status='1',
            tracks=album['tracks'],
            info=album['info'],
            is_mine='0')
        self.write(result)
