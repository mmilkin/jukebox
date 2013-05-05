import json

from klein import Klein
import twisted.internet.defer as defer

import jukebox.storage


class API(object):
    app = Klein()

    def __init__(self, storage=None):
        if not storage:
            storage = jukebox.storage.MemoryStorage()
        self.storage = storage

    def format_song(self, song):
        return {
            'pk': song.pk,
            'title': song.title,
            'album': song.album,
            'artist': song.artist,
        }

    @app.route('/api/all_songs', methods=['GET'])
    @defer.inlineCallbacks
    def all_songs(self, request):
        request.setHeader('Content-Type', 'application/json')
        songs = yield self.storage.get_all_songs()
        data = {'songs': [self.format_song(s) for s in songs]}
        defer.returnValue(json.dumps(data))
