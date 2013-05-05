import itertools

import zope.interface
import twisted.internet.defer as defer


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


class MemoryStorage(object):
    zope.interface.implements(IStorage)

    def __init__(self):
        self._seq = itertools.count(1)
        self._store = {}

    def get_all_songs(self):
        d = defer.Deferred()
        d.callback(self._store.itervalues())
        return d

    def get_song(self, pk):
        d = defer.Deferred()
        try:
            song = self._store[pk]
        except KeyError as e:
           d.errback(e)
           return d
        song.pk = pk
        d.callback(song)
        return d

    def add_song(self, song):
        d = defer.Deferred()
        song.pk = next(self._seq)
        self._store[song.pk] = song
        d.callback(song.pk)
        return d

    def del_song(self, song):
        d = defer.Deferred()
        try:
            del self._store[song.pk]
        except KeyError as e:
            d.errback(e)
            return d
        d.callback(None)
        return d
