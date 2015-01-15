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
            uri='path 1',
        )
        pk = yield storage.add_song(song)
        song_back = yield storage.get_song(pk)

        util.song_assert(song, song_back)

    @defer.inlineCallbacks
    def test_get_song_missing(self):
        storage = self.make_storage()

        with pytest.raises(KeyError):
            yield storage.get_song('-1')

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
        all_songs = list(all_songs)

        songs.sort(key=operator.attrgetter('pk'))
        all_songs.sort(key=operator.attrgetter('pk'))

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
        song = yield storage.get_song(pk)
        yield storage.remove_song(song)

        with pytest.raises(KeyError):
            yield storage.get_song(pk)


class TestMemoryStorage(IStorage, TestCase):
    def make_storage(self):
        return jukebox.storage.MemoryStorage()


class TestMultiStorage(IStorage, TestCase):
    def make_storage(self):
        self.storages = []
        self.storages.append(jukebox.storage.MemoryStorage())
        self.storages.append(jukebox.storage.MemoryStorage())
        self.storages.append(jukebox.storage.MemoryStorage())
        return jukebox.storage.MultiStorage(
            self.storages[0],
            self.storages[1],
            self.storages[2],
        )

    @defer.inlineCallbacks
    def test_multi_get_all(self):
        storage = self.make_storage()
        songs = []
        for i in range(10):
            song = jukebox.song.Song(
                title='song %s' % i,
                album='album %s' % i,
                artist='artist %s' % i,
                uri='path %s' % i,
            )
            song.pk = yield self.storages[i % len(self.storages)].add_song(song)
            songs.append(song)

        all_songs = yield storage.get_all_songs()
        all_songs = list(all_songs)

        songs.sort(key=operator.attrgetter('title'))
        all_songs.sort(key=operator.attrgetter('title'))

        for song1, song2 in zip(songs, all_songs):
            song1.pk = None
            song2.pk = None
            print song1, song2
            util.song_assert(song1, song2)
