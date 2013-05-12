import json

from klein import Klein
import twisted.internet.defer as defer

import jukebox.storage
import jukebox.song


class API(object):
    app = Klein()

    def __init__(self, storage=None, playlist=None):
        if storage is None:
            storage = jukebox.storage.MemoryStorage()
        if playlist is None:
            playlist = jukebox.song.Playlist()
        self.storage = storage
        self.playlist = playlist

    def format_song(self, song):
        if not song:
            return None
        return {
            'pk': song.pk,
            'title': song.title,
            'album': song.album,
            'artist': song.artist,
        }

    @app.route('/songs', methods=['GET'])
    @defer.inlineCallbacks
    def all_songs(self, request):
        request.setHeader('Content-Type', 'application/json')
        songs = yield self.storage.get_all_songs()
        data = {'songs': [self.format_song(s) for s in songs]}
        defer.returnValue(json.dumps(data))

    @app.route('/playlist', methods=['GET'])
    def get_playlist(self, request):
        request.setHeader('Content-Type', 'application/json')
        data = {
            'current': self.format_song(self.playlist.cur),
            'queue': [self.format_song(s) for s in self.playlist]
        }
        return json.dumps(data)

    @app.route('/playlist/add', methods=['POST'])
    @defer.inlineCallbacks
    def add_to_playlist(self, request):
        pk = int(json.loads(request.content.getvalue())['pk'])
        song = yield self.storage.get_song(pk)
        self.playlist.add_song(song)
        defer.returnValue('')

    @app.route('/tickle', methods=['GET'])
    def tickle(self, request):
        d = defer.Deferred()
        def l():
            d.callback('playlist')
        d.l = l # This is a hack to keep the l around as long ad d
        self.playlist.add_listener(l)
        return d
