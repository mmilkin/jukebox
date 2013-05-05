import jukebox.song 


def song_assert(song1, song2):
    assert song1.title == song2.title
    assert song1.album == song2.album
    assert song1.artist == song2.artist
    assert song1.path == song2.path


def test_add_song():
    playlist = jukebox.song.Playlist()
    song = jukebox.song.Song(
        title='song 1',
        album='album 1',
        artist='artist 1',
        path='path 1',
    )
    playlist.add_song(song)
    song_assert(song, playlist.cur)


def test_add_two_songs():
    playlist = jukebox.song.Playlist()
    song1 = jukebox.song.Song(
        title='song 1',
        album='album 1',
        artist='artist 1',
        path='path 1',
    )
    playlist.add_song(song1)
    song_assert(song1, playlist.cur)
    song2 = jukebox.song.Song(
        title='song 2',
        album='album 2',
        artist='artist 2',
        path='path 2',
    )
    playlist.add_song(song2)
    song_assert(song1, playlist.cur)


def test_advance():
    playlist = jukebox.song.Playlist()
    song1 = jukebox.song.Song(
        title='song 1',
        album='album 1',
        artist='artist 1',
        path='path 1',
    )
    playlist.add_song(song1)
    song2 = jukebox.song.Song(
        title='song 2',
        album='album 2',
        artist='artist 2',
        path='path 2',
    )
    playlist.add_song(song2)

    song_assert(playlist.cur, song1)
    playlist.advance()
    song_assert(playlist.cur, song2)
    playlist.advance()
    assert playlist.cur is None

def test_playlist_listener():
    playlist = jukebox.song.Playlist()
    song = None

    def listener():
        assert playlist.cur == song
    playlist.add_listener(listener)

    song1 = jukebox.song.Song(
        title='song 1',
        album='album 1',
        artist='artist 1',
        path='path 1',
    )
    song = song1
    playlist.add_song(song1)
    song2 = jukebox.song.Song(
        title='song 2',
        album='album 2',
        artist='artist 2',
        path='path 2',
    )
    playlist.add_song(song2)

    song = song2
    playlist.advance()

    song = None
    playlist.advance()
