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


def test_source_init_start_song_callback():
    playlist = mock.Mock(name='playlist', cur=None)
    encoder = mock.Mock(name='encoder')
    source = jukebox.httpd.Source(playlist, encoder)
    playlist.add_listener.assert_called_with(source.start_new_song)


def test_add_client_send():
    playlist = mock.Mock(name='playlist', cur=None)
    encoder = mock.Mock(name='encoder')
    source = jukebox.httpd.Source(playlist, encoder)
    client = mock.Mock(name='client')

    source.add_client(client)

    source.send('foo')

    client.send.assert_called_with('foo')


def test_source_new_song():
    playlist = mock.Mock(name='playlist')
    encoder = mock.Mock(name='encoder')
    source = jukebox.httpd.Source(playlist, encoder)
    client = mock.Mock(name='client')

    source.start_new_song('NEW_CUR')
    
    encoder.assert_called_with(
        song=playlist.cur,
        data_callback=source.send,
        done_callback=playlist.advance
    )


def test_source_not_new_song():
    playlist = mock.Mock(name='playlist')
    encoder = mock.Mock(name='encoder')
    source = jukebox.httpd.Source(playlist, encoder)
    client = mock.Mock(name='client')

    source.start_new_song('FOO')
    
    assert not encoder.called


def test_source_new_song_empty_playlist():
    playlist = mock.Mock(name='playlist', cur=None)
    encoder = mock.Mock(name='encoder')
    source = jukebox.httpd.Source(playlist, encoder)
    client = mock.Mock(name='client')

    source.start_new_song('NEW_CUR')
    
    assert not encoder.called
