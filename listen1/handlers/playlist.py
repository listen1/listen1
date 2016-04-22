# coding=utf8
import logging

from handlers.base import BaseHandler
from models.playlist import PlaylistManager
from replay import get_provider, get_provider_list

logger = logging.getLogger('listenone.' + __name__)


class ShowPlaylistHandler(BaseHandler):
    def get(self):
        source = self.get_argument('source', '0')

        provider_list = get_provider_list()
        index = int(source)
        if index >= 0 and index < len(provider_list):
            provider = provider_list[index]
            playlist = provider.list_playlist()
        else:
            playlist = []

        result = dict(result=playlist)
        self.write(result)


class PlaylistHandler(BaseHandler):
    def get(self):
        list_id = self.get_argument('list_id', '')
        if list_id.startswith('my_'):
            playlist = PlaylistManager.shared_instance().get_playlist(list_id)

            info = dict(
                cover_img_url=playlist['cover_img_url'],
                title=playlist['title'], id=playlist['id'])

            result = dict(
                status='1', tracks=playlist['tracks'], info=info, is_mine='1')
        else:
            provider = get_provider(list_id)
            item_id = list_id.split('_')[1]
            result = provider.get_playlist(item_id)
            result.update(dict(is_mine='0'))
        self.write(result)


class AddMyPlaylistHandler(BaseHandler):
    def post(self):
        list_id = self.get_argument('list_id', '')
        track_id = self.get_argument('id', '')
        title = self.get_argument('title', '')
        artist = self.get_argument('artist', '')
        url = self.get_argument('url', '')
        artist_id = self.get_argument('artist_id', '')
        album = self.get_argument('album', '')
        album_id = self.get_argument('album_id', '')
        source = self.get_argument('source', '')
        source_url = self.get_argument('source_url', '')

        track = {
            'id': track_id,
            'title': title,
            'artist': artist,
            'url': url,
            'artist_id': artist_id,
            'album': album,
            'album_id': album_id,
            'source': source,
            'source_url': source_url,
        }

        PlaylistManager.shared_instance().add_track_in_playlist(track, list_id)

        result = dict(result='success')

        self.write(result)


class CreateMyPlaylistHandler(BaseHandler):
    def post(self):
        list_title = self.get_argument('list_title', '')
        track_id = self.get_argument('id', '')
        title = self.get_argument('title', '')
        artist = self.get_argument('artist', '')
        url = self.get_argument('url', '')
        artist_id = self.get_argument('artist_id', '')
        album = self.get_argument('album', '')
        album_id = self.get_argument('album_id', '')
        source = self.get_argument('source', '')
        source_url = self.get_argument('source_url', '')

        track = {
            'id': track_id,
            'title': title,
            'artist': artist,
            'url': url,
            'artist_id': artist_id,
            'album': album,
            'album_id': album_id,
            'source': source,
            'source_url': source_url,
        }

        newlist_id = PlaylistManager.shared_instance()\
            .create_playlist(list_title)

        PlaylistManager.shared_instance()\
            .add_track_in_playlist(track, newlist_id)

        result = dict(result='success')
        self.write(result)


class ShowMyPlaylistHandler(BaseHandler):
    def get(self):
        resultlist = PlaylistManager.shared_instance().\
            list_playlist()
        result = dict(result=resultlist)
        self.write(result)


class ClonePlaylistHandler(BaseHandler):
    def post(self):
        list_id = self.get_argument('list_id', '')
        provider = get_provider(list_id)
        if list_id[2:].startswith('album'):
            album_id = list_id.split('_')[1]
            album = provider.get_album(album_id)
            tracks = album['tracks']
            info = album['info']
        elif list_id[2:].startswith('artist'):
            artist_id = list_id.split('_')[1]
            artist = provider.get_artist(artist_id)
            tracks = artist['tracks']
            info = artist['info']
        elif list_id[2:].startswith('playlist'):
            playlist_id = list_id.split('_')[1]
            playlist = provider.get_playlist(playlist_id)
            tracks = playlist['tracks']
            info = playlist['info']

        list_title = info['title']
        cover_img_url = info['cover_img_url']
        newlist_id = PlaylistManager.shared_instance()\
            .create_playlist(list_title, cover_img_url)
        for track in tracks:
            PlaylistManager.shared_instance()\
                .add_track_in_playlist(track, newlist_id)
        result = dict(result='success')
        self.write(result)


class RemoveTrackHandler(BaseHandler):
    def post(self):
        track_id = self.get_argument('track_id', '')
        list_id = self.get_argument('list_id', '')
        PlaylistManager.shared_instance().remove_track_in_playlist(
            track_id, list_id)
        result = dict(result='success')
        PlaylistManager.shared_instance()
        self.write(result)


class RemoveMyPlaylistHandler(BaseHandler):
    def post(self):
        list_id = self.get_argument('list_id', '')
        PlaylistManager.shared_instance().remove_playlist(list_id)
        result = dict(result='success')
        self.write(result)
