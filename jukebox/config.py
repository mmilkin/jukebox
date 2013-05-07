def make_root_resource():
    from jukebox.api import API
    from jukebox.httpd import HTTPd, Stream, Source
    from jukebox.storage import MemoryStorage
    from jukebox.scanner import DirScanner
    from jukebox.song import Song, Playlist

    storage = MemoryStorage()
    scanner = DirScanner(storage, '/Users/armooo/Documents/')
    scanner.scan()
    playlist = Playlist()
    api_server = API(storage, playlist)
    source = Source(playlist)
    source.start_background()
    httpd = HTTPd(api_server.app.resource(), Stream(source))
    return httpd.app.resource
resource = make_root_resource()
