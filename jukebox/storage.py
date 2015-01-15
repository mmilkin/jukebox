import base64
import copy
import hashlib
import hmac
import itertools
import json
import time
import urllib

from twisted.web.client import Agent, HTTPConnectionPool, readBody, IBodyProducer, BrowserLikeRedirectAgent
from twisted.web.http_headers import Headers
import twisted.internet.defer as defer
import zope.interface

from jukebox.interfaces import IStorage, ISearchableStorage
import jukebox.song


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
        pk = int(pk)
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

    def remove_song(self, song):
        d = defer.Deferred()
        try:
            del self._store[int(song.pk)]
        except KeyError as e:
            d.errback(e)
            return d
        d.callback(None)
        return d


class MultiStorage(object):
    zope.interface.implements(IStorage, ISearchableStorage)

    def __init__(self, primary_storage, *extra_storages):
        self.primary_storage = IStorage(primary_storage)
        self.extra_storages = {
            str(i): IStorage(extra_storage)
            for i, extra_storage in enumerate(extra_storages)
        }
        self.extra_storages['-1'] = self.primary_storage
        self.extra_searchable_storages = {
            str(i): ISearchableStorage(extra_storage)
            for i, extra_storage in enumerate(extra_storages)
        }
        self.extra_searchable_storages['-1'] = ISearchableStorage(primary_storage)

    def patch_song(self, storage_id):
        def func(song):
            song = copy.copy(song)
            song.pk = '{}:{}'.format(storage_id, song.pk)
            return song
        return func

    def patch_songs(self, storage_id):
        patcher = self.patch_song(storage_id)

        def func(songs):
            return [patcher(song) for song in songs]
        return func

    @defer.inlineCallbacks
    def get_all_songs(self):
        results = yield defer.gatherResults(
            [
                storage.get_all_songs().addCallback(self.patch_songs(storage_id))
                for storage_id, storage in self.extra_storages.items()
            ],
            consumeErrors=True,
        )
        songs = [
            song
            for song_list in results
            for song in song_list
        ]
        defer.returnValue(songs)

    def get_song(self, pk):
        try:
            storage_id, pk = pk.split(':', 1)
        except ValueError:
            raise KeyError(pk)
        storage = self.extra_storages[storage_id]
        return storage.get_song(pk).addCallback(self.patch_song(storage_id))

    @defer.inlineCallbacks
    def add_song(self, song):
        pk = yield self.primary_storage.add_song(song)
        defer.returnValue('-1:{}'.format(pk))

    def remove_song(self, song):
        song = copy.copy(song)
        try:
            storage_id, song.pk = song.pk.split(':', 1)
        except ValueError:
            raise KeyError(song.pk)
        storage = self.extra_storages[storage_id]
        return storage.remove_song(song)

    def init(self):
        return defer.gatherResults(
            [storage.init() for storage in self.extra_searchable_storages.values()],
            consumeErrors=True,
        )

    @defer.inlineCallbacks
    def search(self, query):
        results = yield defer.gatherResults(
            [
                storage.search(query).addCallback(self.patch_songs(storage_id))
                for storage_id, storage in self.extra_searchable_storages.items()
            ],
            consumeErrors=True,
        )
        songs = [
            song
            for song_list in results
            for song in song_list
        ]
        defer.returnValue(songs)


class StringProducer(object):
    zope.interface.implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return defer.succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


class GoogleMusicAllAccessStorage(object):
    zope.interface.implements(ISearchableStorage)

    def __init__(self, reactor, username, password, device_id):
        self.username = username
        self.password = password
        self.device_id = str(int(device_id, 16))
        pool = HTTPConnectionPool(reactor)
        pool.maxPersistentPerHost = 8
        self.agent = Agent(reactor, pool=pool)
        self.redirect_agent = BrowserLikeRedirectAgent(self.agent)
        self.auth = None

    @defer.inlineCallbacks
    def init(self):
        data = {
            'accountType': 'HOSTED_OR_GOOGLE',
            'Email': self.username,
            'Passwd': self.password,
            'service': 'sj',
            'source': 'jukebox-0.1',
        }
        responce = yield self.agent.request(
            'POST',
            'https://www.google.com/accounts/ClientLogin',
            Headers({
                'Content-Type': ['application/x-www-form-urlencoded; charset=UTF-8'],
            }),
            StringProducer(urllib.urlencode(data)),
        )
        body = yield readBody(responce)
        if responce.code != 200:
            raise Exception('Login failed {}: {}'.format(responce.code, body))
        for line in body.split('\n'):
            key, value = line.split('=')
            if key == 'Auth':
                self.auth = value
                break
        else:
            raise Exception('Auth not found')

    def authed_get(self, url, args, agent=None, headers=None):
        if not agent:
            agent = self.redirect_agent
        url = url + '?' + urllib.urlencode(args)

        full_headers = Headers({
            'Content-Type': ['application/json'],
            'Authorization': ['GoogleLogin auth={}'.format(self.auth)],
        })
        if headers:
            for k, v in headers.items():
                full_headers.addRawHeader(k, v)

        return agent.request(
            'GET',
            url,
            headers=full_headers,
        )

    @defer.inlineCallbacks
    def _get_songs_for_artist_id(self, artist_id):
        responce = yield self.authed_get(
            'https://mclients.googleapis.com/sj/v1.10/fetchartist',
            {
                'alt': 'json',
                'nid': artist_id,
                'include-albums': False,
                'num-top-tracks': 50,
                'num-related-artists': 0,
            }
        )
        body = yield readBody(responce)
        body = json.loads(body)
        try:
            songs = body['topTracks']
        except KeyError:
            songs = []
        defer.returnValue(songs)

    @defer.inlineCallbacks
    def _get_songs_for_album_id(self, album_id):
        responce = yield self.authed_get(
            'https://mclients.googleapis.com/sj/v1.10/fetchalbum',
            {
                'alt': 'json',
                'nid': album_id,
                'include-tracks': True,
            }
        )
        body = yield readBody(responce)
        body = json.loads(body)
        try:
            songs = body['tracks']
        except KeyError:
            songs = []
        defer.returnValue(songs)

    def make_song(self, song_data):
        song_id = song_data['storeId']
        song = jukebox.song.Song(
            title=song_data['title'],
            album=song_data['album'],
            artist=song_data['artist'],
            uri=lambda: self.get_song_url(song_id),
        )
        song.pk = 'gmaa:' + song_id
        return song

    @defer.inlineCallbacks
    def search(self, query):
        responce = yield self.authed_get(
            'https://mclients.googleapis.com/sj/v1.10/query',
            {'q': query, 'max-results': 50, }
        )
        body = yield readBody(responce)
        if responce.code != 200:
            raise Exception('Search failed {}: {}'.format(responce.code, body))
        result = json.loads(body)
        songs = []
        defereds = []

        for entry in result.get('entries', []):
            if entry['type'] == '1':
                songs.append(entry['track'])
            if entry['type'] == '2':
                d = self._get_songs_for_artist_id(entry['artist']['artistId'])
                defereds.append(d)
            if entry['type'] == '3':
                d = self._get_songs_for_album_id(entry['album']['albumId'])
                defereds.append(d)

        results = yield defer.DeferredList(defereds)

        for success, result in results:
            if success:
                songs.extend(result)
            else:
                print result

        defer.returnValue([self.make_song(song) for song in songs])

    @defer.inlineCallbacks
    def get_song_url(self, song_id):
        s1 = base64.b64decode('VzeC4H4h+T2f0VI180nVX8x+Mb5HiTtGnKgH52Otj8ZCGDz9jRW'
                              'yHb6QXK0JskSiOgzQfwTY5xgLLSdUSreaLVMsVVWfxfa8Rw==')
        s2 = base64.b64decode('ZAPnhUkYwQ6y5DdQxWThbvhJHN8msQ1rqJw0ggKdufQjelrKuiG'
                              'GJI30aswkgCWTDyHkTGK9ynlqTkJ5L4CiGGUabGeo8M6JTQ==')
        key = ''.join([chr(ord(c1) ^ ord(c2)) for (c1, c2) in zip(s1, s2)])
        salt = str(int(time.time() * 1000))
        m = hmac.new(key, song_id, hashlib.sha1)
        m.update(salt)
        sig = base64.urlsafe_b64encode(m.digest())[:-1]

        responce = yield self.authed_get(
            'https://android.clients.google.com/music/mplay',
            {
                'opt': 'hi',
                'net': 'wifi',
                'pt': 'e',
                'slt': salt,
                'sig': sig,
                'mjck': song_id,
            },
            agent=self.agent,
            headers={'X-Device-ID': self.device_id}
        )
        print responce.headers
        url = responce.headers.getRawHeaders('location')[0]
        print url
        defer.returnValue(url)

    @defer.inlineCallbacks
    def get_song(self, pk):
        if not pk.startswith('gmaa:'):
            raise Exception('Bad PK {}'.format(pk))

        song_id = pk.split(':', 1)[1]
        responce = yield self.authed_get(
            'https://mclients.googleapis.com/sj/v1.10/fetchtrack',
            {'alt': 'json', 'nid': song_id}
        )
        body = yield readBody(responce)
        if responce.code != 200:
            raise Exception('Search failed {}: {}'.format(responce.code, body))
        song = self.make_song(json.loads(body))
        defer.returnValue(song)
