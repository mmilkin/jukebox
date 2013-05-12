import json

import mock
from twisted.trial.unittest import TestCase
import twisted.internet.defer as defer

import jukebox.api
import jukebox.storage
import jukebox.song

import util


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
            path='path 1',
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
                path='path %s' % i,
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


def test_get_playlist_queue():
    request = mock.Mock(name='request')
    playlist = jukebox.song.Playlist()
    songs = []
    for i in range(3):
        song = jukebox.song.Song(
            title='song %s' % i,
            album='album %s' % i,
            artist='artist %s' % i,
            path='path %s' % i,
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
        path='path 0',
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
    playlist = jukebox.song.Playlist()
    storage = jukebox.storage.MemoryStorage()
    song = jukebox.song.Song(
        title='song 0',
        album='album 0',
        artist='artist 0',
        path='path 0',
    )
    storage.add_song(song)
    api = jukebox.api.API(playlist=playlist, storage=storage)
    api.add_to_playlist(request)

    util.song_assert(song, playlist.cur)
