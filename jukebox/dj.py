import random
import zope.interface


from jukebox.interfaces import IDJ, IStorage


class RandomDJ(object):
    zope.interface.classProvides(IDJ)

    def __init__(self, storage, playlist):
        self.storage = IStorage(storage)
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
