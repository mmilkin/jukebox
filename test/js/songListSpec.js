(function () {
'use strict';

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

        it('should create the "music" model from xhr', function() {
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

    });
});

})();
