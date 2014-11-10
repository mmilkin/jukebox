def song_assert(song1, song2):
    assert song1.title == song2.title
    assert song1.album == song2.album
    assert song1.artist == song2.artist
    assert song1.uri == song2.uri
