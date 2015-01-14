import zope.interface


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


class ISearchableStorage(zope.interface.Interface):
    def init():
        """
        Returns a Deferred that fires when the ISearchableStorage is ready to be used
        """

    def search(query):
        """
        Returns a Deferred with an iterable of the Song instances in this ISearchableStorage.
        """

    def get_song(pk):
        """
        Returns a Deferred with a single Song by pk.
        """


class IDJ(zope.interface.Interface):
    def __call__(storage, playlist):
        """
        Picks songs from the storage to add to the playlist.
        """


class IEncoder(zope.interface.Interface):
    """
    An IEncoder takes raw song data and transforms it in to an audio stream. It
    is also responsible for limiting the playback speed.
    """
    def __init__(song, data_callback):
        """
        song: A instance of song object

        data_callback: a callable which will be called with each fragment of
            encoded data

        done_callback: a zero argument callable which is called when the song
            is over
        """

    def encode():
        """
        Returns a Deferred that fires when this song is done
        """


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
