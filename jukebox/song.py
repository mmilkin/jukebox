class Song(object):
    def __init__(self, title, album, artist, path):
        self.pk = None
        self.title = title
        self.album = album
        self.artist = artist
        self.path = path

    def __repr__(self):
        return '<Song(pk={}, title={}>'.format(self.pk, self.title)


class Playlist(object):
    def __init__(self):
        self.cur = None
        self._list = []
        self._listeners = []

    def __iter__(self):
        return iter(self._list)

    def add_song(self, song):
        self._list.append(song)
        if not self.cur:
            self.advance()

    def advance(self):
        old_cur = self.cur
        try:
            self.cur = self._list.pop(0)
        except IndexError:
            self.cur = None

        if old_cur != self.cur:
            self._notify()

    def add_listener(self, listener):
        self._listeners.append(listener)

    def _notify(self):
        for listener in self._listeners:
            listener()

    def __repr__(self):
        songs = ', '.join([repr(s) for s in self])
        return u'<Playlist [%s]>' % songs
