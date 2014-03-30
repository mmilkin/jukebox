from twisted.internet import defer
import urllib


class Song(object):
    def __init__(self, title, album, artist, uri):
        self.pk = None
        self.title = title
        self.album = album
        self.artist = artist
        self._uri = uri

    def get_uri(self):
        if not callable(self._uri):
            uri = lambda: self._uri
        else:
            uri = self._uri
        return defer.maybeDeferred(uri)

    def __repr__(self):
        return '<Song(pk={}, title={}>'.format(self.pk, self.title)

    def open(self):
        return open(self.path)

    def stream(self, filesrc):
        filesrc.set_property('location', self.path)


class GoogleSong(Song):
    def __init__(self, google_song, web_api):
        self.instance = google_song
        self.web_api = web_api
        super(GoogleSong, self).__init__(
            google_song['title'],
            google_song['album'],
            google_song['artist'],
            None
        )
        self.path = None
        self.pk = google_song['id']

    def open(self):
        return urllib.urlopen(self.get_uri())

    def get_uri(self):
        urls = self.web_api.get_stream_urls(self.pk)
        # Normal tracks return a single url, All Access tracks return multiple urls,
        # which must be combined and are not supported
        if len(urls) == 1:
            return urls[0]
        return None

    def stream(self, filesrc):
        """
        Get the a stream to the first url for google song
        """
        urls = self.web_api.get_stream_urls(self.pk)
        if len(urls) == 0:
            filesrc.set_property('uri', self.path)


class Playlist(object):
    def __init__(self):
        self.cur = None
        self._list = []
        self._listeners = set()

    def __iter__(self):
        return iter(self._list)

    def add_song(self, song):
        self._list.append(song)
        if not self.cur:
            self.advance()
        self._notify('PLAYLIST_CHANGE')

    def advance(self):
        try:
            self.cur = self._list.pop(0)
        except IndexError:
            self.cur = None
        self._notify('NEW_CUR')

    def add_listener(self, listener):
        self._listeners.add(listener)

    def del_listener(self, listener):
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _notify(self, event):
        for listener in self._listeners.copy():
            listener(event)

    def __repr__(self):
        songs = ', '.join([repr(s) for s in self])
        return u'<Playlist [%s]>' % songs
