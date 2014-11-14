(function () {
    'use strict';

    var module = angular.module('accounts', ['ng']);

    module.controller('addAccountCtl',  ['$scope', '$http', function($scope, $http) {
        $scope.submit = function (data) {
            event.preventDefault();
            var config = {
                method: 'post',
                url: 'api/google-account',
                data: {
                    user: $scope.username,
                    password: $scope.password
                }
            };
            $http(config).then(function (result) {
                $scope.username = '';
                $scope.password = '';
            });
        };

    }]);
})();