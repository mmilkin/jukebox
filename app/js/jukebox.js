(function () {
    'use strict';

    angular.module('templates', []);

    var module = angular.module('jukebox', [
        'playlist',
        'songList',
        'tickle',
        'templates',
        'accounts'
    ]);

    module.run(function(tickleService) {
        console.log('run');
    });

})();
