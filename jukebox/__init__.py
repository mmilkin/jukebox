from jukebox.api import API
from jukebox.storage import MemoryStorage
from jukebox.song import Song

def make_root_resource():
    storage = MemoryStorage()
    for i in range(10):
        song = Song(
            title='song %s' % i,
            album='album %s' % i,
            artist='artist %s' % i,
            path='path %s' % i,
        )
        storage.add_song(song)
    api_server = API(storage)
    return api_server.app.resource
resource = make_root_resource()
