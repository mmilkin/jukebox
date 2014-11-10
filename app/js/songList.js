(function () {
    'use strict';

    var module = angular.module('songList', ['ng']);

    module.filter('groupByArtist', function() {
        return function(songs) {
            return _.groupBy(songs, 'artist');
        };
    });

    module.filter('searchSongs', function() {
        return function(songs, query) {
            if (angular.isUndefined(query)) {
                return songs;
            }

            function matchField(field, song) {
                if (!song[field]) {
                    return true;
                }
                return song[field].toLowerCase().indexOf(query) !== -1;
            }

            function filter(song) {
                return (
                    matchField('artist', song) ||
                    matchField('album', song) ||
                    matchField('title', song)
                );
            }

            return _.filter(songs, filter);
        };
    });

    module.controller('songListCtl', function($scope, $http) {
        var songs = [];

        $http.get('/api/songs').then(function (result) {
            $scope.songs = result.data.songs;
        });

        $scope.play = function (pk) {
            $http.post('/api/playlist/add', {pk: pk});
        };

        $scope.$on('artistShown', function(e) {
            e.stopPropagation();
            $scope.$broadcast('closeArtist');
        });

    });

    module.controller('artistCtl', function($scope, $anchorScroll, $location) {
        $scope.shown = false;

        $scope.toggleShown = function() {
            if ( !$scope.shown ) {
                $scope.$emit('artistShown');
            }
            $scope.shown = !$scope.shown;
        };

        $scope.$on('closeArtist', function() {
            $scope.shown = false;
        });
    });

})();
