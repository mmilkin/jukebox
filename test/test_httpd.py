import mock
import twisted.web.server

import jukebox.httpd


def test_stream_get():
    request = mock.Mock(name='request')
    source = mock.Mock(name='source', spec=jukebox.httpd.Source)
    Client = mock.Mock(name='Client')

    stream = jukebox.httpd.Stream(source, Client)
    result = stream.render_GET(request)

    assert twisted.web.server.NOT_DONE_YET == result
    Client.assert_called_with(request)
    source.add_client.assert_called_with(Client.return_value)


def test_client_init():
    request = mock.Mock(name='request')

    client = jukebox.httpd.Client(request)

    request.setHeader.assert_called_with('Content-Type', 'audio/mpeg')


def test_client_send():
    request = mock.Mock(name='request')

    client = jukebox.httpd.Client(request)
    client.send('foo')

    request.write.assert_called_with('foo')


def test_source_init_start_file():
    playlist = mock.Mock(name='playlist', cur=None)
    source = jukebox.httpd.Source(playlist)
    playlist.add_listener.assert_called_with(source.start_new_file)


def test_source_start_new_file_none():
    playlist = mock.Mock(name='playlist', cur=None)
    source = jukebox.httpd.Source(playlist)
    source.file = 'foo'

    source.start_new_file('NEW_CUR')

    assert None == source.file


@mock.patch('__builtin__.open')
def test_source_start_new_file(open):
    playlist = mock.Mock(name='playlist')
    source = jukebox.httpd.Source(playlist)
    source.file = None

    source.start_new_file('NEW_CUR')

    assert open.return_value == source.file
    open.assert_called_with(playlist.cur.path, 'rb')


def test_add_client_send():
    playlist = mock.Mock(name='playlist', cur=None)
    source = jukebox.httpd.Source(playlist)
    client = mock.Mock(name='client')

    source.add_client(client)

    source.send('foo')

    client.send.assert_called_with('foo')


def test_process_file_none():
    playlist = mock.Mock(name='playlist', cur=None)
    source = jukebox.httpd.Source(playlist)
    client = mock.Mock(name='client')

    source.add_client(client)
    source.process_file()

    assert False == client.send.called


@mock.patch('__builtin__.open')
def test_source_start_new_file(open):
    playlist = mock.Mock(name='playlist')
    source = jukebox.httpd.Source(playlist)
    source.file = None
    client = mock.Mock(name='client')

    source.start_new_file('NEW_CUR')
    source.add_client(client)
    source.process_file()

    file = open.return_value

    file.read.assert_called_with(8192)
    client.send.assert_called_with(file.read.return_value)
