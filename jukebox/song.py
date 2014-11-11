class Song(object):
    def __init__(self, title, album, artist, uri):
        self.pk = None
        self.title = title
        self.album = album
        self.artist = artist
        self.uri = uri

    def __repr__(self):
        return '<Song(pk={}, title={}>'.format(self.pk, self.title)


class GoogleSong(Song):
    def __init__(self, google_song, web_api):
        self.instance = google_song
        self.web_api = web_api
        self.title = google_song['title']
        self.album = google_song['album']
        self.artist = google_song['artist']
        self.pk = self.id = google_song['id']

    @property
    def uri(self):
        urls = self.web_api.get_stream_urls(self.id)
        # Normal tracks return a single url, All Access tracks return multiple urls,
        # which must be combined and are not supported
        if len(urls) == 1:
            return urls[0]
        raise Exception(u'Bad Url')


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
