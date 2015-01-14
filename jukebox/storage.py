import itertools

import zope.interface
import twisted.internet.defer as defer

from jukebox.interfaces import IStorage, ISearchableStorage


class NoOpStorageAdaptor(object):
    zope.interface.implements(IStorage)
    __used_for__ = ISearchableStorage

    def __init__(self, context):
        self.context = context

    def get_song(self, pk):
        return self.context.get_song(pk)

    def get_all_songs(self):
        return defer.succeed([])

    def add_song(self, song):
        return defer.fail(Exception('Sorry I can\'t do that'))

    def remove_song(self, song):
        return defer.fail(Exception('Sorry I can\'t do that'))


class NoOpSearchableStorage(object):
    zope.interface.implements(ISearchableStorage)
    __used_for__ = IStorage

    def __init__(self, context):
        self.context = context

    def init(self):
        return defer.succeed(None)

    def search(self, query):
        return defer.succeed([])

    def get_song(self, pk):
        return self.context.get_song(pk)


class MemoryStorage(object):
    zope.interface.implements(IStorage)

    def __init__(self):
        self._seq = itertools.count(1)
        self._store = {}

    def get_all_songs(self):
        d = defer.Deferred()
        d.callback(self._store.copy().itervalues())
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
