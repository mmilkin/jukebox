import os
import zope.interface
import mutagen

import jukebox.song


class IScanner(zope.interface.Interface):
    def scan():
        """
        Start the scanning process. It is expected to be called at startup and
        can block.
        """

    def watch():
        """
        Starts an async watcher that can add files to the IStorage
        """

    def stop():
        """
        Stops the async watcher
        """


class DirScanner(object):
    zope.interface.implements(IScanner)

    def __init__(self, storage, path):
        self.storage = storage
        self.path = path

    def scan(self):
        for root, dirs, files in os.walk(self.path):
            for name in files:
                path = os.path.join(root, name)
                music_file = mutagen.File(path, easy=True)
                if not music_file:
                    continue
                self.storage.add_song(jukebox.song.Song(
                    title=(music_file.get('title', []) + [None])[0],
                    album=(music_file.get('album', []) + [None])[0],
                    artist=(music_file.get('artist', []) + [None])[0],
                    path=path,
                ))

    def watch(self):
        pass

    def stop(self):
        pass
