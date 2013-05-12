import operator

import pytest
from twisted.trial.unittest import TestCase
import twisted.internet.defer as defer

import jukebox.storage
import jukebox.song

import util


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
            path='path 1',
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
                path='path %s' % i,
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
                path='path %s' % i,
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
            path='path 1',
        )
        pk = yield storage.add_song(song)
        yield storage.del_song(song)

        with pytest.raises(KeyError):
          yield storage.get_song(pk)


class TestMemoryStorage(IStorage, TestCase):
    def make_storage(self):
        return jukebox.storage.MemoryStorage()
