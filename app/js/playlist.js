(function() {
    'use strict';

    var module = angular.module('playlist', ['ng']);

    module.controller('playlistCtl', ['$scope', '$http', function($scope, $http) {
        $http.get('/api/playlist').then(function (result) {
            $scope.current = result.data.current;
            $scope.songs = result.data.queue;
        });
    }]);
})();
