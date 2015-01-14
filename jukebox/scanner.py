import os
import zope.interface
import mutagen

import jukebox.song
from jukebox.interfaces import IScanner


class DirScanner(object):
    zope.interface.implements(IScanner)

    def __init__(self, storage, *paths):
        self.storage = storage
        self.paths = paths

    def _scan_path(self, path):
        for root, dirs, files in os.walk(path):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    music_file = mutagen.File(file_path, easy=True)
                except:
                    continue
                if not music_file:
                    continue

                try:
                    title = music_file['title'][0]
                except (KeyError, IndexError):
                    title = None
                try:
                    album = music_file['album'][0]
                except (KeyError, IndexError):
                    album = None
                try:
                    artist = music_file['artist'][0]
                except (KeyError, IndexError):
                    artist = None

                self.storage.add_song(jukebox.song.Song(
                    title=title,
                    album=album,
                    artist=artist,
                    uri='file://' + file_path,
                ))

    def scan(self):
        for path in self.paths:
            self._scan_path(path)

    def watch(self):
        pass

    def stop(self):
        pass
