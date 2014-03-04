import itertools

import zope.interface
from twisted.internet.defer import (
    Deferred,
    DeferredList,
    inlineCallbacks,
    returnValue
)



class IStorage(zope.interface.Interface):
    def get_all_songs():
        """
        Returns a Deferred with an iterable of the Song instances in this IStorage.
        """

    def get_song(pk):
        """
        Returns a Deferred with a single Song by pk.
        """

    def add_song(song):
        """
        Adds a single Song to this IStorage instance.
        Returns a Deferred which with the new PK
        """

    def remove_song(song):
        """
        Removes a single Song to this IStorage instance.
        Returns a Deferred which fires None when complete
        """


class MultiPartStorage(object):
    zope.interface.implements(IStorage)

    def _filter_out_errors(self, values):
        return [differed_callback[1] for differed_callback in values if differed_callback[0]]

    def __init__(self, storage=None):
        if storage:
            self._storage = storage
        else:
            self._storage = [MemoryStorage()]

    @inlineCallbacks
    def get_all_songs(self):
        all_songs_results = yield DeferredList(
            [storage.get_all_songs() for storage in self._storage], consumeErrors=True
        )
        all_songs = []
        error_list = []
        for success, songs in all_songs_results:
            if success:
                all_songs.extend(songs)
            else:
                error_list.extend(songs)

        if all_songs:
            returnValue(all_songs)
        elif error_list:
            raise error_list[0]

        returnValue(all_songs)

    @inlineCallbacks
    def get_song(self, pk):
        songs_results = yield DeferredList([storage.get_song(pk) for storage in self._storage], consumeErrors=True)
        error = None
        for success, song in songs_results:
            if success:
                returnValue(song)
            else:
                error = song
        raise error

    @inlineCallbacks
    def add_song(self, song):
        added_song = yield self._storage[0].add_song(song)
        returnValue(added_song)

    @inlineCallbacks
    def del_song(self, song):
        removed_songs = yield DeferredList([storage.del_song(song) for storage in self._storage], consumeErrors=True)

        error = None
        for success, removed_songs in removed_songs:
            if success:
                returnValue(removed_songs)
            else:
                error = removed_songs

        raise error


class MemoryStorage(object):
    zope.interface.implements(IStorage)

    def __init__(self):
        self._seq = itertools.count(1)
        self._store = {}

    def get_all_songs(self):
        d = Deferred()
        d.callback(self._store.copy().itervalues())
        return d

    def get_song(self, pk):
        d = Deferred()
        try:
            song = self._store[pk]
        except KeyError as e:
            d.errback(e)
            return d
        song.pk = pk
        d.callback(song)
        return d

    def add_song(self, song):
        d = Deferred()
        song.pk = next(self._seq)
        self._store[song.pk] = song
        d.callback(song.pk)
        return d

    def del_song(self, song):
        d = Deferred()
        try:
            del self._store[song.pk]
        except KeyError as e:
            d.errback(e)
            return d
        d.callback(None)
        return d
