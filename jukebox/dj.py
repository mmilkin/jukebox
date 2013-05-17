import random
import zope.interface


class IDJ(zope.interface.Interface):
    def __call__(storage, playlist):
        """
        Picks songs from the storage to add to the playlist.
        """


class RandomDJ(object):
    zope.interface.classProvides(IDJ)

    def __init__(self, storage, playlist):
        self.storage = storage
        self.playlist = playlist
        self.playlist.add_listener(self.playlist_changed)
        self.playlist_changed(None)

    def playlist_changed(self, event):
        length = len(list(self.playlist))
        if length >= 5:
            return

        def add_song(songs):
            songs = list(songs)
            if not songs:
                return
            self.playlist.add_song(random.choice(songs))

        songs = self.storage.get_all_songs()
        songs.addCallback(add_song)
