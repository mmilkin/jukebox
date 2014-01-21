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
                    module: 'templates'
                },
                src: ['app/partial/*.html'],
                dest: 'build/templates.js'
            },
        },
        concat: {
            js: {
                src: [].concat(['app/lib/angular.js', 'app/lib/*.js'], jsFiles, ['build/templates.js']),
                dest: 'build/app.concat.js'
            }
        },
        ngmin: {
            app: {
                src: 'build/app.concat.js',
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
        less: {
            development: {
                options: {
                    dumpLineNumbers: 'all'
                },
                files: {
                    'static/style.css': 'app/style.less'
                }
            },
            production: {
                options: {
                    yuicompress: true
                },
                files: {
                    'static/style.css': 'app/style.less'
                }
            }
        },
        watch: {
            templates: {
                files: 'app/partial/*.html',
                tasks: ['ngtemplates', 'concat', 'copy:js']
            },
            scripts: {
                files: [].concat(jsFiles, testFiles),
                tasks: ['jshint', 'karma:watch:run', 'concat', 'ngmin', 'copy:js']
            },
            css: {
                files: [].concat('app/style.less'),
                tasks: ['less:development']
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
    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-karma');
    grunt.loadNpmTasks('grunt-ngmin');

    grunt.registerTask('default', ['jshint', 'karma:once', 'ngtemplates', 'concat', 'ngmin', 'less:development', 'copy']);
    grunt.registerTask('prod', ['jshint', 'karma:once', 'ngtemplates', 'concat', 'ngmin', 'uglify', 'less:production', 'copy:html']);
    grunt.registerTask('watch-test', ['karma:watch', 'watch']);
};
