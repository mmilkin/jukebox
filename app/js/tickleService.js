(function(){
'use strict';

var module = angular.module('tickle', ['ng']);


module.factory('tickleService', ['$http', '$rootScope', '$timeout',
               function($http, $rootScope, $timeout) {
    var retry = function() {
        $rootScope.$broadcast('tickle');
        wait();
    };
    var wait = function() {
        $http.get('/api/tickle').then(function(result){
            $rootScope.$broadcast('tickle', result.data);
            wait();
        }, function() {
            $timeout(retry, 1000);
        });
    };

    wait();
}]);

})();
