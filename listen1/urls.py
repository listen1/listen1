from handlers.douban import DBFavoriteHandler, DBLoginHandler, \
    ValidCodeHandler, DBLogoutHandler
from handlers.home import HomeHandler
from handlers.player import AlbumHandler, ArtistHandler
from handlers.playlist import AddMyPlaylistHandler, ClonePlaylistHandler, \
    CreateMyPlaylistHandler, PlaylistHandler, \
    RemoveMyPlaylistHandler, RemoveTrackHandler, \
    ShowMyPlaylistHandler, ShowPlaylistHandler
from handlers.search import SearchHandler
from handlers.trackfile import TrackFileHandler


url_patterns = [
    (r"/", HomeHandler),

    (r"/search", SearchHandler),

    # player handlers
    (r"/playlist", PlaylistHandler),
    (r"/artist", ArtistHandler),
    (r"/album", AlbumHandler),

    # track proxy
    (r"/track_file", TrackFileHandler),

    # playlist
    (r"/show_playlist", ShowPlaylistHandler),
    (r"/add_myplaylist", AddMyPlaylistHandler),
    (r"/create_myplaylist", CreateMyPlaylistHandler),
    (r"/show_myplaylist", ShowMyPlaylistHandler),
    (r"/remove_track_from_myplaylist", RemoveTrackHandler),
    (r"/remove_myplaylist", RemoveMyPlaylistHandler),
    (r"/clone_playlist", ClonePlaylistHandler),

    # douban handlers
    (r"/dbvalidcode", ValidCodeHandler),
    (r"/dblogin", DBLoginHandler),
    (r"/dblogout", DBLogoutHandler),
    (r"/dbfav", DBFavoriteHandler),
]
