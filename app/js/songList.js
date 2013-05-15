(function () {
    'use strict';

    var module = angular.module('songList', ['ng', 'ui.if']);

    module.controller('songListCtl', ['$scope', '$http', function($scope, $http) {
        $http.get('/api/songs').then(function (result) {
            $scope.songs = result.data.songs;
            $scope.artists = _.groupBy($scope.songs, 'artist');
        });

        $scope.play = function (pk) {
            $http.post('/api/playlist/add', {pk: pk});
        };

        $scope.$on('artistShown', function(e) {
            e.stopPropagation();
            $scope.$broadcast('closeArtist');
        });

    }]);

    module.controller('artistCtl', ['$scope', '$anchorScroll', '$location',
                      function($scope, $anchorScroll, $location) {
        $scope.shown = false;

        $scope.toggleShown = function() {
            if ( !$scope.shown ) {
                $scope.$emit('artistShown');
                $location.hash($scope.$index);
                $anchorScroll();
            }
            $scope.shown = !$scope.shown;
        };

        $scope.$on('closeArtist', function() {
            $scope.shown = false;
        });
    }]);

})();
