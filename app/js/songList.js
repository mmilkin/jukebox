(function () {
    'use strict';

    var module = angular.module('songList', ['ng']);

    module.controller('songListCtl', ['$scope', '$http', function($scope, $http) {
        $http.get('/api/songs').then(function (result) {
            $scope.songs = result.data.songs;
        });

        $scope.play = function (pk) {
            $http.post('/api/playlist/add', {pk: pk});
        };
    }]);
})();
