def song_assert(song1, song2):
    assert song1.title == song2.title
    assert song1.album == song2.album
    assert song1.artist == song2.artist
    # This hack only works because the deferrers were created with success
    assert song1.get_uri().result == song2.get_uri().result
