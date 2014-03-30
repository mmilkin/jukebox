import operator

import pytest
from twisted.trial.unittest import TestCase
import twisted.internet.defer as defer

import jukebox.storage
from jukebox.storage import GoogleAuthenticationError
import jukebox.song

import util
from mock import patch, Mock


class IStorage(object):
    def make_storage(self):
        raise NotImplementedError()

    @defer.inlineCallbacks
    def test_add_get_song(self):
        storage = self.make_storage()
        song = jukebox.song.Song(
            title='song 1',
            album='album 1',
            artist='artist 1',
            uri='path 1',
        )
        pk = yield storage.add_song(song)
        song_back = yield storage.get_song(pk)

        util.song_assert(song, song_back)

    @defer.inlineCallbacks
    def test_get_song_missing(self):
        storage = self.make_storage()

        with pytest.raises(KeyError):
            yield storage.get_song(-1)

    @defer.inlineCallbacks
    def test_multi_add_get(self):
        storage = self.make_storage()
        for i in range(10):
            song = jukebox.song.Song(
                title='song %s' % i,
                album='album %s' % i,
                artist='artist %s' % i,
                uri='path %s' % i,
            )
            song.pk = yield storage.add_song(song)

        song_back = yield storage.get_song(song.pk)

        util.song_assert(song, song_back)

    @defer.inlineCallbacks
    def test_multi_add_get_all(self):
        storage = self.make_storage()
        songs = []
        for i in range(10):
            song = jukebox.song.Song(
                title='song %s' % i,
                album='album %s' % i,
                artist='artist %s' % i,
                uri='path %s' % i,
            )
            song.pk = yield storage.add_song(song)
            songs.append(song)

        all_songs = yield storage.get_all_songs()

        sorted(songs, key=operator.attrgetter('pk'))
        sorted(all_songs, key=operator.attrgetter('pk'))

        for song1, song2 in zip(songs, all_songs):
            util.song_assert(song1, song2)

    @defer.inlineCallbacks
    def test_remove_song(self):
        storage = self.make_storage()
        song = jukebox.song.Song(
            title='song 1',
            album='album 1',
            artist='artist 1',
            uri='path 1',
        )
        pk = yield storage.add_song(song)
        yield storage.del_song(song)

        with pytest.raises(KeyError):
          yield storage.get_song(pk)


class TestMemoryStorage(IStorage, TestCase):
    def make_storage(self):
        return jukebox.storage.MemoryStorage()


class TestGoogleMultiStorage(IStorage, TestCase):

    def setUp(self):
        super(TestGoogleMultiStorage, self).setUp()
        patch_mobile_client = patch('jukebox.storage.Mobileclient').start()
        patch_web_client = patch('jukebox.storage.Webclient').start()

        self.mock_web_client = Mock(name='web_client')
        self.mock_mobile_client = Mock(name='mobile_client')
        self.mock_mobile_client.get_all_songs.return_value = []

        patch_web_client.return_value = self.mock_web_client
        patch_mobile_client.return_value = self.mock_mobile_client

    def tearDown(self):
        super(TestGoogleMultiStorage, self).setUp()
        patch.stopall()

    def make_storage(self):
        return jukebox.storage.GooglePlayStorage('some', 'password')

    def test_called_login(self):
        jukebox.storage.GooglePlayStorage('some', 'password')
        self.mock_mobile_client.login.assert_called_with('some', 'password')
        self.mock_web_client.login.assert_called_with('some', 'password')
        self.assertTrue(self.mock_mobile_client.is_authenticated.called)
        self.assertTrue(self.mock_web_client.is_authenticated.called)

    def test_web_auth_failed(self):
        storage = jukebox.storage.GooglePlayStorage('some', 'password')
        self.mock_web_client.is_authenticated.return_value = False
        self.assertRaises(GoogleAuthenticationError, storage._login)

    def test_mobile_auth_failed(self):
        storage = jukebox.storage.GooglePlayStorage('some', 'password')
        self.mock_mobile_client.is_authenticated.return_value = False
        self.assertRaises(GoogleAuthenticationError, storage._login)

    def test_load_all_songs_no_auth(self):
        storage = jukebox.storage.GooglePlayStorage('some', 'password')
        self.mock_mobile_client.is_authenticated.return_value = False
        self.assertRaises(GoogleAuthenticationError, storage._load_songs)

    def test_load_all_songs(self):
        self.mock_mobile_client.get_all_songs.return_value = [
            {'title': 'song 1', 'album': 'album', 'artist': 'some dude', 'id': '12345'}
        ]

        storage = jukebox.storage.GooglePlayStorage('some', 'password')

        self.assertTrue(self.mock_mobile_client.get_all_songs.called)
        self.assertEqual(len(storage._store), 1)
        self.assertTrue('12345' in storage._store)
        song = storage._store['12345']

        self.assertEqual(song.title, 'song 1')
        self.assertEqual(song.album, 'album')
        self.assertEqual(song.artist, 'some dude')
        self.assertEqual(song.pk, '12345')
        self.assertEqual(song.web_api, storage.web_client)
