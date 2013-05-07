import os
import mock
import jukebox.scanner


@mock.patch('mutagen.File')
@mock.patch('os.walk')
def test_dir_scanner_scan(walk, File):
    walk.return_value = [
        ('base', [], ['file_name']),
    ]
    File.return_value = {
        'title': ['fun1', 'fun2'],
        'album': [],
        'artist': ['bob'],
    }
    storage = mock.Mock(name='storage')
    scanner = jukebox.scanner.DirScanner(storage, 'path') 

    scanner.scan()

    walk.assert_called_with('path')
    File.assert_called_with(os.path.join('base', 'file_name'), easy=True)
    song = storage.add_song.call_args[0][0]
    assert 'fun1' == song.title
    assert None == song.album
    assert 'bob' == song.artist
