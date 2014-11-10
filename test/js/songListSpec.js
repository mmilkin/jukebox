(function () {
'use strict';

describe('groupByArtist filter', function () {
    beforeEach(module('songList'));

    var injected = {};
    beforeEach(inject(function (groupByArtistFilter) {
        injected.groupByArtist = groupByArtistFilter;
    }));

    it('should group by artist', function () {
        var songs = [
            {
                pk: 0,
                title: 'song 0',
                album: 'album 0',
                artist: 'artist 0'
            },
            {
                pk: 1,
                title: 'song 1',
                album: 'album 0',
                artist: 'artist 0'
            },
            {
                pk: 2,
                title: 'song 2',
                album: 'album 1',
                artist: 'artist 1'
            }
        ];

        var groupedSongs = injected.groupByArtist(songs);

        expect(groupedSongs['artist 0'][0].pk).toEqual(0);
        expect(groupedSongs['artist 0'][1].pk).toEqual(1);
        expect(groupedSongs['artist 1'][0].pk).toEqual(2);
    });
});


describe('searchSongs', function() {
    beforeEach(module('songList'));

    var injected = {};
    beforeEach(inject(function (searchSongsFilter) {
        injected.searchSongs = searchSongsFilter;
    }));

    var songs = [
        {
            pk: 0,
            title: 'song 0',
            album: 'album 0',
            artist: 'artist 0'
        },
        {
            pk: 1,
            title: 'song 1',
            album: 'album 1',
            artist: 'artist 1'
        },
        {
            pk: 2,
            title: undefined,
            album: null,
            artist: null
        }
    ];

    it('should match all with a undefined search', function () {
        var result = injected.searchSongs(songs, undefined);
        expect(result[0].pk).toEqual(0);
        expect(result[1].pk).toEqual(1);
        expect(result[2].pk).toEqual(2);
        expect(result.length).toEqual(3);
    });

    it('should match by title', function () {
        var result = injected.searchSongs(songs, 'song 0');
        expect(result[0].pk).toEqual(0);
        expect(result[1].pk).toEqual(2);
        expect(result.length).toEqual(2);
    });

    it('should match by album', function () {
        var result = injected.searchSongs(songs, 'album 1');
        expect(result[0].pk).toEqual(1);
        expect(result[1].pk).toEqual(2);
        expect(result.length).toEqual(2);
    });

    it('should match by artist', function () {
        var result = injected.searchSongs(songs, 'artist 0');
        expect(result[0].pk).toEqual(0);
        expect(result[1].pk).toEqual(2);
        expect(result.length).toEqual(2);
    });
});

describe('songList controllers', function () {
    beforeEach(module('songList'));

    describe('songList controller', function () {

        var injected = {};
        beforeEach(inject(function($httpBackend, $rootScope, $controller) {
            injected.$httpBackend = $httpBackend;
            injected.$rootScope = $rootScope;
            injected.$controller = $controller;
        }));

        afterEach(function() {
            injected.$httpBackend.verifyNoOutstandingExpectation();
            injected.$httpBackend.verifyNoOutstandingRequest();
        });

        it('should create the "songs" model from xhr', function () {
            injected.$httpBackend.expectGET('/api/songs').respond(
                {songs: [
                    {
                        pk: 0,
                        title: 'song 0',
                        album: 'album 0',
                        artist: 'artist 0'
                    },
                    {
                        pk: 1,
                        title: 'song 1',
                        album: 'album 1',
                        artist: 'artist 1'
                    }
                ]});

            var scope = injected.$rootScope.$new();

            var ctrl = injected.$controller('songListCtl', {$scope: scope});

            injected.$httpBackend.flush();

            expect(scope.songs[0].pk).toEqual(0);
            expect(scope.songs[0].title).toEqual('song 0');
            expect(scope.songs[0].album).toEqual('album 0');
            expect(scope.songs[0].artist).toEqual('artist 0');

            expect(scope.songs[1].pk).toEqual(1);
            expect(scope.songs[1].title).toEqual('song 1');
            expect(scope.songs[1].album).toEqual('album 1');
            expect(scope.songs[1].artist).toEqual('artist 1');
        });

        it('should POST to /api/playlist/add when play is called', function() {
            injected.$httpBackend.expectGET('/api/songs').respond({songs: []});
            injected.$httpBackend.expectPOST(
                '/api/playlist/add',
                 '{"pk":333}'
            ). respond(200);

            var scope = injected.$rootScope.$new();
            var ctrl = injected.$controller('songListCtl', {$scope: scope});

            scope.play(333);

            injected.$httpBackend.flush();
        });

        it('should reflect a artistShown into a closeArtist', function() {
            injected.$httpBackend.expectGET('/api/songs').respond({songs: []});

            var scope = injected.$rootScope.$new();
            var innerScope = scope.$new();
            var ctrl = injected.$controller('songListCtl', {$scope: scope});

            var fired = false;

            innerScope.$on('closeArtist', function() { fired=true; });
            innerScope.$emit('artistShown');

            expect(fired).toBeTruthy();
            injected.$httpBackend.flush();
        });

    });

    describe('artistCtl controller', function () {

        var injected = {};
        beforeEach(inject(function($httpBackend, $rootScope, $controller) {
            injected.$rootScope = $rootScope;
            injected.$controller = $controller;
        }));

        it('should emit artistShown when toggled', function() {
            var scope = injected.$rootScope.$new();
            var innerScope = scope.$new();
            var ctrl = injected.$controller(
                'artistCtl',
                {$scope: innerScope}
            );

            var fired = false;
            scope.$on('artistShown', function() {
                fired = true;
            });

            innerScope.toggleShown();

            expect(fired).toBeTruthy();
        });

        it('should not be shown on closeArtist', function() {
            var scope = injected.$rootScope.$new();
            var innerScope = scope.$new();
            var ctrl = injected.$controller(
                'artistCtl',
                {$scope: innerScope}
            );

            innerScope.shown = true;

            scope.$broadcast('closeArtist');

            expect(innerScope.shown).toBeFalsy();
        });

    });
});

})();
