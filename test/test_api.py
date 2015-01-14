import json

from twisted.trial.unittest import TestCase
from zope.interface import directlyProvides
import mock
import twisted.internet.defer as defer

import jukebox.api
import jukebox.interfaces
import jukebox.song
import jukebox.storage


class TestAllSongs(TestCase):
    @defer.inlineCallbacks
    def test_empty(self):
        request = mock.Mock(name='request')
        storage = jukebox.storage.MemoryStorage()
        api = jukebox.api.API(storage=storage)

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
            uri='path 1',
        )
        request = mock.Mock(name='request')
        storage = jukebox.storage.MemoryStorage()
        pk = yield storage.add_song(song)
        api = jukebox.api.API(storage=storage)

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
                uri='path %s' % i,
            )
            pk = yield storage.add_song(song)
            pks.append(pk)
        api = jukebox.api.API(storage=storage)

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


class TestSearchSongs(TestCase):
    @defer.inlineCallbacks
    def test_search_songs(self):
        request = mock.Mock(name='request')
        request.args = {'q': ['foo']}
        storage = mock.Mock(name='storage')
        directlyProvides(storage, jukebox.interfaces.ISearchableStorage)
        songs = []
        for i in range(3):
            song = jukebox.song.Song(
                title='song %s' % i,
                album='album %s' % i,
                artist='artist %s' % i,
                uri='path %s' % i,
            )
            song.pk = i
            songs.append(song)
        storage.search.return_value = defer.succeed(songs)

        api = jukebox.api.API(storage=storage)

        result = yield api.search_songs(request)

        request.setHeader.assert_called_with(
            'Content-Type', 'application/json'
        )

        assert result == json.dumps({'songs': [
            {
                'pk': 0,
                'title': 'song 0',
                'album': 'album 0',
                'artist': 'artist 0',
            },
            {
                'pk': 1,
                'title': 'song 1',
                'album': 'album 1',
                'artist': 'artist 1',
            },
            {
                'pk': 2,
                'title': 'song 2',
                'album': 'album 2',
                'artist': 'artist 2',
            },
        ]})


def test_get_playlist_queue():
    request = mock.Mock(name='request')
    playlist = jukebox.song.Playlist()
    songs = []
    for i in range(3):
        song = jukebox.song.Song(
            title='song %s' % i,
            album='album %s' % i,
            artist='artist %s' % i,
            uri='path %s' % i,
        )
        songs.append(song)
        playlist.add_song(song)

    api = jukebox.api.API(playlist=playlist)
    json_playlist = api.get_playlist(request)

    request.setHeader.assert_called_with(
        'Content-Type', 'application/json'
    )
    assert [
        {
            'pk': None,
            'title': 'song 1',
            'album': 'album 1',
            'artist': 'artist 1',
        },
        {
            'pk': None,
            'title': 'song 2',
            'album': 'album 2',
            'artist': 'artist 2',
        },
    ] == json.loads(json_playlist)['queue']


def test_get_playlist_queue_empty():
    request = mock.Mock(name='request')
    playlist = jukebox.song.Playlist()
    api = jukebox.api.API(playlist=playlist)
    json_playlist = api.get_playlist(request)

    request.setHeader.assert_called_with(
        'Content-Type', 'application/json'
    )
    assert [] == json.loads(json_playlist)['queue']


def test_get_playlist_current():
    request = mock.Mock(name='request')
    playlist = jukebox.song.Playlist()
    songs = []
    song = jukebox.song.Song(
        title='song 0',
        album='album 0',
        artist='artist 0',
        uri='path 0',
    )
    songs.append(song)
    playlist.add_song(song)

    api = jukebox.api.API(playlist=playlist)
    json_playlist = api.get_playlist(request)

    request.setHeader.assert_called_with(
        'Content-Type', 'application/json'
    )
    assert {
        'pk': None,
        'title': 'song 0',
        'album': 'album 0',
        'artist': 'artist 0',
    } == json.loads(json_playlist)['current']


def test_get_playlist_current_none():
    request = mock.Mock(name='request')
    playlist = jukebox.song.Playlist()
    api = jukebox.api.API(playlist=playlist)
    json_playlist = api.get_playlist(request)

    request.setHeader.assert_called_with(
        'Content-Type', 'application/json'
    )
    assert None == json.loads(json_playlist)['current']


def test_add_to_play_list():
    request = mock.Mock(name='request')
    request.content.getvalue.return_value = '{"pk": 1}'
    playlist = mock.Mock(name='playlist')
    storage = mock.Mock(name='storage')
    directlyProvides(storage, jukebox.interfaces.IStorage)
    song = storage.get_song.return_value

    api = jukebox.api.API(playlist=playlist, storage=storage)
    api.add_to_playlist(request)

    storage.get_song.assert_called_with(1)
    playlist.add_song.assert_called_with(song)


class TestTickle(TestCase):
    @defer.inlineCallbacks
    def test_tickle(self):
        request = mock.Mock(name='request')
        playlist = mock.Mock(name='playlist')

        def call(l):
            l('FOO')
        playlist.add_listener.side_effect = call

        api = jukebox.api.API(playlist=playlist, storage=None)
        result = yield api.tickle(request)
        assert result == 'playlist'
