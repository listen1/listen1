# coding=utf8
import json
import logging

from settings import MEDIA_ROOT

logger = logging.getLogger('listenone.' + __name__)


class Playlist(object):
    def __init__(self):
        self.cover_img_url = ''
        self.title = ''
        self.play_count = 0
        self.list_id = ''

manager_instance = None


class PlaylistManager(object):

    default_path = MEDIA_ROOT + '/user/' + 'playlist.json'

    @classmethod
    def shared_instance(cls):
        global manager_instance
        if manager_instance is None:
            manager_instance = PlaylistManager()
        return manager_instance

    def __init__(self, path=None):
        self.path = self.default_path if path is None else path
        try:
            self.load_from_disk()
            self.nextid = 1
            for l in self.mylists:
                listid = int(l['id'].split('_')[1])
                if listid >= self.nextid:
                    self.nextid = listid + 1
        except:
            self.mylists = []
            self.nextid = 1

    def save_to_disk(self):
        s = json.dumps(self.mylists)
        with open(self.path, 'w') as f:
            f.write(s)

    def load_from_disk(self):
        with open(self.path, 'r') as f:
            s = f.read()
        self.mylists = json.loads(s)

    def get_playlist(self, list_id):
        targetlist = None
        for playlist in self.mylists:
            if playlist['id'] == list_id:
                targetlist = playlist
                break
        return targetlist

    def create_playlist(
            self, title, cover_img_url='/static/images/mycover.jpg',
            tracks=None):
        newlist_id = 'my_' + str(self.nextid)
        if tracks is None:
            my_tracks = []
        else:
            my_tracks = tracks
        newlist = dict(
            title=title,
            id=newlist_id,
            cover_img_url=cover_img_url,
            tracks=my_tracks)
        self.nextid += 1
        self.mylists.append(newlist)
        self.save_to_disk()
        return newlist_id

    def list_playlist(self):
        resultlist = []
        for l in self.mylists:
            r = dict(
                cover_img_url=l['cover_img_url'],
                title=l['title'],
                play_count=0,
                list_id=l['id'],)
            resultlist.append(r)
        return resultlist

    def remove_playlist(self, list_id):
        target_index = -1
        for index, playlist in enumerate(self.mylists):
            if playlist['id'] == list_id:
                target_index = index
                break
        self.mylists = self.mylists[:target_index] + \
            self.mylists[target_index + 1:]
        self.save_to_disk()

    def is_exist_in_playlist(self, track_id, list_id):
        playlist = self.get_playlist(list_id)
        for d in playlist['tracks']:
            if d['id'] == track_id:
                return True
        return False

    def add_track_in_playlist(self, track, list_id):
        track_id = track['id']
        if self.is_exist_in_playlist(track_id, list_id):
            return
        playlist = self.get_playlist(list_id)
        playlist['tracks'].append(track)
        self.save_to_disk()

    def remove_track_in_playlist(self, track_id, list_id):
        playlist = self.get_playlist(list_id)
        target_index = -1
        for index, d in enumerate(playlist['tracks']):
            if d['id'] == track_id:
                target_index = index
                break
        playlist['tracks'] = playlist['tracks'][:target_index] + \
            playlist['tracks'][target_index + 1:]
