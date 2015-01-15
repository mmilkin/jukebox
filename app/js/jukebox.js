(function () {
    'use strict';

    angular.module('templates', ['angularSpinner']);

    var module = angular.module('jukebox', [
        'playlist',
        'songList',
        'tickle',
        'templates'
    ]);

    module.run(function(tickleService) {
        console.log('run');
    });

})();
