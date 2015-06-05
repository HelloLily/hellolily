'use strict';

// Imports
var cleanhtml = require('gulp-cleanhtml');  // strip whitespace eg.
var concat = require('gulp-concat');  // merge file stream to one file
var del = require('del');  // remove files/dirs
var gulp = require('gulp');  // base module
var livereload = require('gulp-livereload');  // live reload server (needs plugin install in Chrome)
var rebaseUrls = require('gulp-css-rebase-urls'); // get css url links and rewrites them
var rename = require('gulp-rename');  // rename current file stream
var sourcemaps = require('gulp-sourcemaps');  // create sourcemaps from original files and create a .map file
var templateCache = require('gulp-angular-templatecache');  // create out of html files Angular templates in one js file/stream
var uglify = require('gulp-uglify');  // minify javascript file
var uglifyCss = require('gulp-uglifycss');  // minify css file
var wrap = require('gulp-wrap');  // surround current file(s) with other content (IIFE eg.)

/**
 * Config for Gulp
 */
var config = {
    buildDir: 'lily/static/build',
    templates: {
        src: 'frontend/app/**/*.html',
        module: 'app.templates',
        fileName: 'templates.js'
    },
    appJs: {
        src: [
            'frontend/app/**/module.js',
            'frontend/app/**/*.js'
        ],
        minifiedFileName: 'app.min.js',
        devFileName: 'app.dev.js'
    },
    vendorJs: {
        src: [
            'frontend/vendor/**/*jquery.min.js',
            'frontend/vendor/**/*angular.js',
            'frontend/vendor/**/*.js'
        ],
        minifiedFileName: 'vendor.min.js',
        devFileName: 'vendor.dev.js'
    },
    appCss: {
        src: 'frontend/app/**/*.css',
        root: 'frontend',
        minifiedFileName: 'app.min.css',
        devFileName: 'app.dev.css'
    },
    vendorCss: {
        src: [
            'frontend/vendor/metronic/assets/global/plugins/bootstrap/css/bootstrap.css',
            'frontend/vendor/metronic/assets/global/plugins/select2/select2.css',
            'frontend/vendor/metronic/assets/global/plugins/select2/select2-bootstrap.css',
            'frontend/vendor/**/*.css'
        ],
        root: 'frontend',
        minifiedFileName: 'vendor.min.css',
        devFileName: 'vendor.dev.css'
    },
    vendorAssets: {
        src: [
            'frontend/vendor/**/*.*',
            '!frontend/vendor/**/*.css',
            '!frontend/vendor/**/*.js'
        ],
        buildDir: 'lily/static/build/vendor'
    }
};

/**
 * Create a minified file of app Javascript files
 *
 * Call:
 *      gulp app:js
 *
 * Actions:
 *      - get js files
 *      - create a sourcemap from original files
 *      - wraps all files in IIFE
 *      - concat all files to one file
 *      - uglify file
 *
 * Outcome:
 *      - production file
 *      - sourcemap file
 *      - livereload call
 */
gulp.task('app:js', function () {
    return gulp.src(config.appJs.src)
        .pipe(sourcemaps.init())
        .pipe(wrap('(function(angular){\n\'use strict\';\n<%= contents %>\n})(angular);'))
        .pipe(concat(config.appJs.minifiedFileName))
        .pipe(uglify())
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(config.buildDir))
        .pipe(livereload());
});

/**
 * Create a minified file of Angular Template files
 *
 * Call:
 *      gulp app:templates
 *
 * Actions:
 *      - clean html
 *      - create js file from angular templates
 *      - wraps file in IIFE
 *      - uglify file
 *
 * Outcome:
 *      - production file
 *      - livereload call
 */
gulp.task('app:templates', function () {
    return gulp.src(config.templates.src)
        // clean whitespace
        .pipe(cleanhtml())
        // Turn into Angular templates
        .pipe(templateCache(config.templates.fileName, {module: config.templates.module, standalone:true}))
        .pipe(wrap('(function(angular){\n\'use strict\';\n<%= contents %>\n})(angular);'))
        .pipe(uglify())
        .pipe(gulp.dest(config.buildDir))
        .pipe(livereload());
});

/**
 * Create a minified file of vendor Javascript files
 *
 * Call:
 *      gulp vendor:js
 *
 * Actions:
 *      - create a sourcemap from original files
 *      - concat all files to one file
 *      - uglify file
 *
 * Outcome:
 *      - production file
 *      - sourcemap file§
 *      - livereload call
 */
gulp.task('vendor:js', function () {
    return gulp.src(config.vendorJs.src)
        .pipe(sourcemaps.init())
        .pipe(concat(config.vendorJs.minifiedFileName))
        .pipe(uglify())
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(config.buildDir))
        .pipe(livereload());
});

/**
 * Create a minified file of app css files
 *
 * Call:
 *      gulp app:css
 *
 * Actions:
 *      - create a sourcemap from original files
 *      - rebase src urls in file to correct path
 *      - concat all files to one file
 *      - uglify file
 *
 * Outcome:
 *      - production file
 *      - sourcemap file
 *      - livereload call
 */
gulp.task('app:css', function () {
    return gulp.src(config.appCss.src)
        .pipe(sourcemaps.init())
        .pipe(rebaseUrls({root: config.appCss.root}))
        .pipe(concat(config.appCss.minifiedFileName))
        .pipe(uglifyCss())
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(config.buildDir))
        .pipe(livereload());
});

/**
 * Create a minified file of vendor css files
 *
 * Call:
 *      gulp vendor:css
 *
 * Actions:
 *      - create a sourcemap from original files
 *      - rebase src urls in file to correct path
 *      - concat all files to one file
 *      - uglify file
 *
 * Outcome:
 *      - production file
 *      - sourcemap file
 *      - livereload call
 */
gulp.task('vendor:css', function () {
    return gulp.src(config.vendorCss.src)
        .pipe(sourcemaps.init())
        .pipe(rebaseUrls({root: config.vendorCss.root}))
        .pipe(concat(config.vendorCss.minifiedFileName))
        .pipe(uglifyCss())
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(config.buildDir))
        .pipe(livereload());
});

/**
 * Move non js or css vendor files to build dir
 *
 * Call:
 *      gulp vendor:assets
 *
 * Outcome:
 *      - files moved
 */
gulp.task('vendor:assets', function () {
   return gulp.src(config.vendorAssets.src)
       .pipe(gulp.dest(config.vendorAssets.buildDir))
       .pipe(livereload());
});

/**
 * Clean build dir
 */
gulp.task('clean', function() {
    return del([config.buildDir]);
});

/**
 * Watch relevant dirs for rebuilding & livereload
 */
gulp.task('watch', ['default'], function() {
    livereload.listen();
    gulp.watch(config.templates.src, ['app:templates']);
    gulp.watch(config.appJs.src, ['app:js']);
    gulp.watch(config.appCss.src, ['app:css']);
    gulp.watch(config.vendorJs.src, ['vendor:js']);
    gulp.watch(config.vendorCss.src, ['vendor:css']);
    gulp.watch(config.vendorAssets.src, ['vendor:assets']);
});

gulp.task('default', ['app:js', 'app:css', 'app:templates', 'vendor:js', 'vendor:assets', 'vendor:css'], function() {});
