(function() {
    'use strict';

    var module = angular.module('playlist', ['ng']);

    module.controller('playlistCtl', ['$scope', '$http', function($scope, $http) {
        var load = function() {
            $http.get('/api/playlist').then(function (result) {
                $scope.current = result.data.current;
                $scope.songs = result.data.queue;
            });
        };

        $scope.$on('tickle', load);

        load();
    }]);
})();
