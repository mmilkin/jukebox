'use strict';

module.exports = function(grunt) {
    var jsFiles = ['app/js/*.js'];

    grunt.initConfig({
        jshint: {
            all: jsFiles
        },
        ngtemplates: {
            build: {
                options: {
                    base: 'app/partial',
                    prepend: '/partial/',
                    module: 'jukebox'
                },
                src: ['app/partial/*.html'],
                dest: 'build/templates.js'
            },
        },
        concat: {
            js: {
                src: [].concat(['app/lib/*.js'], jsFiles, ['build/templates.js']),
                dest: 'static/app.js'
            }
        },
        copy: {
            html: {
                files: [ { expand: true, cwd:'app/', src: ['*.html'], dest: 'static/' } ]
            }
        },
        watch: {
            templates: {
                files: 'app/partial/*.html',
                tasks: ['ngtemplates']
            },
            scripts: {
                files: [].concat(jsFiles, ['build/templates.js']),
                tasks: ['jshint', 'concat', 'copy']
            },
            html: {
                files: 'app/*.html',
                tasks: ['copy:html']
            }
        }
    });

    grunt.loadNpmTasks('grunt-angular-templates');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('default', ['jshint', 'ngtemplates', 'concat', 'copy']);
};
