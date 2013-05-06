(function () {
    'use strict';

    var module = angular.module('song_list', ['ng']);

    module.controller('songListCtl', ['$scope', '$http', function($scope, $http) {
        $http.get('/api/songs').then(function (result) {
            $scope.songs = result.data.songs;
        });
    }]);
})();
