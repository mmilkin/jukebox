'use strict';

module.exports = function(grunt) {
    var jsFiles = ['app/js/*.js'];
    var testFiles = ['test/js/*.js'];

    grunt.initConfig({
        jshint: {
            options: {
                jshintrc: '.jshintrc'
            },
            all: [].concat(jsFiles, testFiles)
        },
        karma: {
            watch: {
                configFile: 'karma.conf',
                background: true
            },
            once: {
                configFile: 'karma.conf',
                singleRun: true,
            }
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
                dest: 'build/app.js'
            }
        },
        copy: {
            html: {
                files: [ { expand: true, cwd:'app/', src: ['*.html'], dest: 'static/' } ]
            },
            js: {
                files: [ { expand: true, cwd:'build/', src: ['app.js'], dest: 'static/' } ]
            }
        },
        uglify: {
            js: {
                src: 'build/app.js',
                dest: 'static/app.js'
            }
        },
        watch: {
            templates: {
                files: 'app/partial/*.html',
                tasks: ['ngtemplates', 'concat', 'copy:js']
            },
            scripts: {
                files: [].concat(jsFiles, testFiles),
                tasks: ['jshint', 'karma:watch:run', 'concat', 'copy:js']
            },
            html: {
                files: 'app/*.html',
                tasks: ['copy:html']
            },
        }
    });

    grunt.loadNpmTasks('grunt-angular-templates');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-karma');

    grunt.registerTask('default', ['jshint', 'karma:once', 'ngtemplates', 'concat', 'copy']);
    grunt.registerTask('prod', ['jshint', 'karma:once', 'ngtemplates', 'concat', 'uglify', 'copy:html']);
    grunt.registerTask('test-watch', ['karma:watch', 'watch']);
};
