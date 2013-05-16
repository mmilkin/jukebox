import mock

import jukebox.encoders


"""
@mock.patch('__builtin__.open')
def test_source_start_new_file(open):
    playlist = mock.Mock(name='playlist')
    source = jukebox.httpd.Source(playlist)
    source.file = None

    source.start_new_file('NEW_CUR')

    assert open.return_value == source.file
    open.assert_called_with(playlist.cur.path, 'rb')
"""


