import json

import mock
from twisted.trial.unittest import TestCase
import twisted.internet.defer as defer

import jukebox.api
import jukebox.storage
import jukebox.song


class TestAllSongs(TestCase):
    @defer.inlineCallbacks
    def test_empty(self):
        request = mock.Mock(name='request')  
        storage = jukebox.storage.MemoryStorage()
        api = jukebox.api.API(storage)

        result = yield api.all_songs(request)

        request.setHeader.assert_called_with(
            'Content-Type', 'application/json'
        )
        assert result == json.dumps({'songs': []})

    @defer.inlineCallbacks
    def test_one_songs(self):
        song = jukebox.song.Song(
            title='song 1',
            album='album 1',
            artist='artist 1',
            path='path 1',
        )
        request = mock.Mock(name='request')  
        storage = jukebox.storage.MemoryStorage()
        pk = yield storage.add_song(song)
        api = jukebox.api.API(storage)

        result = yield api.all_songs(request)

        request.setHeader.assert_called_with(
            'Content-Type', 'application/json'
        )

        assert result == json.dumps({'songs': [{
            'pk': pk,
            'title': 'song 1',
            'album': 'album 1',
            'artist': 'artist 1',
        }]})

    @defer.inlineCallbacks
    def test_few_songs(self):
        request = mock.Mock(name='request')  
        storage = jukebox.storage.MemoryStorage()
        pks = []
        for i in range(3):
            song = jukebox.song.Song(
                title='song %s' % i,
                album='album %s' % i,
                artist='artist %s' % i,
                path='path %s' % i,
            )
            pk = yield storage.add_song(song)
            pks.append(pk)
        api = jukebox.api.API(storage)

        result = yield api.all_songs(request)

        request.setHeader.assert_called_with(
            'Content-Type', 'application/json'
        )

        assert result == json.dumps({'songs': [
            {
                'pk': pks[0],
                'title': 'song 0',
                'album': 'album 0',
                'artist': 'artist 0',
            },
            {
                'pk': pks[1],
                'title': 'song 1',
                'album': 'album 1',
                'artist': 'artist 1',
            },
            {
                'pk': pks[2],
                'title': 'song 2',
                'album': 'album 2',
                'artist': 'artist 2',
            },
        ]})
