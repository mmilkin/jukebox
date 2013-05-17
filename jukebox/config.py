def make_root_resource():
    from twisted.internet import reactor

    from jukebox.api import API
    from jukebox.httpd import HTTPd, Stream, Source
    from jukebox.storage import MemoryStorage
    from jukebox.scanner import DirScanner
    from jukebox.song import Song, Playlist
    from jukebox.encoders import CopyEncoder, GSTEncoder
    from jukebox.dj import RandomDJ

    storage = MemoryStorage()
    scanner = DirScanner(storage, '/Users/armooo/Documents/')
    #scanner = DirScanner(storage, '/Volumes/more_music/')
    reactor.callInThread(scanner.scan)
    playlist = Playlist()
    dj = RandomDJ(storage, playlist)
    api_server = API(storage, playlist)
    source = Source(playlist, GSTEncoder)
    httpd = HTTPd(api_server.app.resource(), Stream(source))
    return httpd.app.resource
resource = make_root_resource()
