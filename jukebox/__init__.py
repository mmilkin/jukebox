from jukebox.api import API
from jukebox.httpd import HTTPd
from jukebox.storage import MemoryStorage
from jukebox.song import Song, Playlist

def make_root_resource():
    storage = MemoryStorage()
    playlist = Playlist()
    for i in range(10):
        song = Song(
            title='song %s' % i,
            album='album %s' % i,
            artist='artist %s' % i,
            path='path %s' % i,
        )
        storage.add_song(song)
        if i < 5:
            playlist.add_song(song)

    api_server = API(storage, playlist)
    httpd = HTTPd(api_server.app.resource())
    return httpd.app.resource
resource = make_root_resource()
