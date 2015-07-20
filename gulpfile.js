'use strict';

// Imports
var cached = require('gulp-cached');  // Only work on changed files
var cdnizer = require('gulp-cdnizer'); // Prepend CDN url to resources
var cleanhtml = require('gulp-cleanhtml');  // strip whitespace eg.
var concat = require('gulp-concat');  // merge file stream to one file
var del = require('del');  // remove files/dirs
var gulp = require('gulp');  // base module
var fs = require('fs');  // File system
var imagemin = require('gulp-imagemin');  // Minify/optimize images
var livereload = require('gulp-livereload');  // live reload server (needs plugin install in Chrome)
var merge = require('merge-stream');  // Merge multiple gulp streams together
var path = require('path');  // File path helpers
var rebaseUrls = require('gulp-css-rebase-urls');  // Make relative paths absolute
var remember = require('gulp-remember');  // Remember all files after a cached call
var rename = require('gulp-rename');  // rename current file stream
var sass = require('gulp-sass');  // Sass compilation
var sourcemaps = require('gulp-sourcemaps');  // create sourcemaps from original files and create a .map file
var templateCache = require('gulp-angular-templatecache');  // create out of html files Angular templates in one js file/stream
var uglify = require('gulp-uglify');  // minify javascript file
var uglifyCss = require('gulp-uglifycss');  // minify css file
var watch = require('gulp-watch');  // Optimized file change watcher
var wrap = require('gulp-wrap');  // surround current file(s) with other content (IIFE eg.)

/**
 * Config for Gulp
 */
var config = {
    app: {
        buildDir: 'lily/static/',
        js: {
            src: [
                'frontend/app/**/module.js',
                'frontend/app/**/*.js',
                '!frontend/app/**/*Spec.js',
                '!frontend/app/base/analytics.js'
            ],
            fileName: 'app.js',
            analytics: {
                src: [
                    'frontend/app/base/analytics.js'
                ],
                fileName: 'analytics.js'
            }
        },
        sass: {
            src: ['frontend/app/**/*.scss'],
            base: 'frontend/app/app.scss',
            fileName: 'app.css'
        },
        templates: {
            src: [
                'frontend/app/**/*.html'
            ],
            fileName: 'templates.js',
            module: 'app.templates'
        },
        assets: {
            src: [
                'frontend/app/**/*.*',
                '!frontend/app/**/*.css',
                '!frontend/app/**/*.scss',
                '!frontend/app/**/*.js',
                '!frontend/app/**/*.html'
            ]
        }
    },
    vendor: {
        buildDir: 'lily/static/vendor/',
        js: {
            src: [
                'frontend/vendor/**/*jquery.min.js',
                'frontend/vendor/**/*angular.js',
                'frontend/vendor/**/*.js',
                '!frontend/vendor/**/angular-mocks.js',
                '!frontend/vendor/metronic/assets/global/plugins/ie-fixes/**/*.js'  // IE fixes
            ],
            fileName: 'vendor.js',
            IEFixes: {
                src: [
                    'frontend/vendor/metronic/assets/global/plugins/ie-fixes/**/*.js'
                ],
                fileName: 'ie-fixes.js'
            }
        },
        css: {
            src: [
                'frontend/vendor/metronic/assets/global/plugins/bootstrap/css/bootstrap.css',
                'frontend/vendor/metronic/assets/global/plugins/select2/select2.css',
                'frontend/vendor/metronic/assets/global/plugins/select2/select2-bootstrap.css',
                'frontend/vendor/**/*.css'
            ],
            fileName: 'vendor.css'
        },
        assets: {
            src: [
                'frontend/vendor/**/*.*',
                '!frontend/vendor/**/*.css',
                '!frontend/vendor/**/*.scss',
                '!frontend/vendor/**/*.js',
                '!frontend/vendor/**/*.html'
            ]
        }
    },
    cdn: {
        defaultBase: process.env.STATIC_URL,  // static url to prepend to all file paths.
        root: 'frontend/',
        src: [
            '**/*.{gif,png,jpg,jpeg,svg,ico}',  // Images
            '**/*.{eot,otf,ttf,woff,woff2}',  // Fonts with all types of crud on the back
            '**/*.{eot,otf,ttf,woff,woff2}?*',
            '**/*.{eot,otf,ttf,woff,woff2}#*',
            '**/*.{css,js}'  // Files
        ],
        images: {
            optimizationLevel: 3,
            multipass: true
        }
    }
};

/**
 * Clean build dir
 */
gulp.task('clean', [], function() {
    return del([
        'lily/static/'
    ]);
});

gulp.task('app-js', [], function() {
    return gulp.src(config.app.js.src)
        .pipe(sourcemaps.init())

        .pipe(cached('app-js'))
        .pipe(wrap('(function(angular){\'use strict\';<%= contents %>})(angular);'))
        .pipe(uglify())
        .pipe(remember('app-js'))

        .pipe(concat(config.app.js.fileName))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(config.app.buildDir))
        .pipe(livereload());
});

gulp.task('app-css', [], function() {
    return gulp.src(config.app.sass.base)
        .pipe(sass().on('error', sass.logError))
        .pipe(rebaseUrls({root: config.cdn.root}))
        .pipe(cdnizer({
            defaultCDNBase: config.cdn.defaultBase,
            files: config.cdn.src
        }))
        .pipe(sourcemaps.init({loadMaps: true}))
        .pipe(uglifyCss())
        .pipe(rename(config.app.sass.fileName))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(config.app.buildDir))
        .pipe(livereload());
});

/**
 * App templates
 */
gulp.task('app-templates', [], function() {
    return gulp.src(config.app.templates.src)
        .pipe(cdnizer({
            defaultCDNBase: config.cdn.defaultBase,
            files: config.cdn.src
        }))
        .pipe(cleanhtml())
        .pipe(templateCache(config.app.templates.fileName, {module: config.app.templates.module, standalone:true}))
        .pipe(wrap('(function(angular){\'use strict\';<%= contents %>})(angular);'))
        .pipe(uglify())
        .pipe(gulp.dest(config.app.buildDir))
        .pipe(livereload());
});

gulp.task('app-assets', [], function(){
    return gulp.src(config.app.assets.src)
        .pipe(imagemin({
            optimizationLevel: config.cdn.images.optimizationLevel,
            multipass: config.cdn.images.multipass
        }))
        .pipe(gulp.dest(config.app.buildDir))
        .pipe(livereload());
});

/**
 * Concatenate and minify all vendor static
 */
gulp.task('vendor-js', [], function() {
    return gulp.src(config.vendor.js.src)
        .pipe(sourcemaps.init())

        .pipe(cached('vendor-js'))
        .pipe(uglify())
        .pipe(remember('vendor-js'))

        .pipe(concat(config.vendor.js.fileName))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(config.vendor.buildDir))
        .pipe(livereload());
});

gulp.task('ie-fixes', [], function(){
    return gulp.src(config.vendor.js.IEFixes.src)
        .pipe(sourcemaps.init())
        .pipe(uglify())
        .pipe(concat(config.vendor.js.IEFixes.fileName))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(config.vendor.buildDir))
        .pipe(livereload());
});

gulp.task('vendor-css', [], function() {
    return gulp.src(config.vendor.css.src)
        .pipe(sourcemaps.init())

        .pipe(cached('vendor-css'))
        .pipe(rebaseUrls({root: config.cdn.root}))
        .pipe(cdnizer({
            defaultCDNBase: config.cdn.defaultBase,
            files: config.cdn.src
        }))
        .pipe(uglifyCss())
        .pipe(remember('vendor-css'))

        .pipe(concat(config.vendor.css.fileName))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(config.vendor.buildDir))
        .pipe(livereload());
});

gulp.task('vendor-assets', [], function() {
    return gulp.src(config.vendor.assets.src)
        .pipe(imagemin({
            optimizationLevel: config.cdn.images.optimizationLevel,
            multipass: config.cdn.images.multipass
        }))
        .pipe(gulp.dest(config.vendor.buildDir))
        .pipe(livereload());
});

gulp.task('analytics', [], function() {
    // TODO: please remove this in the future
    return gulp.src(config.app.js.analytics.src)
        .pipe(rename(config.app.js.analytics.fileName))
        .pipe(gulp.dest(config.app.buildDir));
});

/**
 * Concatenate, minify and make source maps of all js and css
 */
gulp.task('build', ['app-js', 'app-css', 'app-templates', 'app-assets', 'vendor-js', 'vendor-css', 'vendor-assets', 'analytics', 'ie-fixes'], function() {});

/**
 * Watch for changes
 */
gulp.task('watch', [], function() {
    livereload.listen();

    // Watch for changes in app javascript
    watch(config.app.js.src, function() {
        gulp.start('app-js');
    });

    // Watch for changes in sass files
    watch(config.app.sass.src, function() {
        gulp.start('app-css')
    });

    // Make our app templates
    watch(config.app.templates.src, function() {
        gulp.start('app-templates');
    });

    // Gather all other static from the app
    watch(config.app.assets.src, function() {
        gulp.start('app-assets');
    });

    // Watch google analytics script
    watch(config.app.js.analytics.src, function() {
        gulp.start('analytics');
    });

    // Recompile all vendor js
    watch(config.vendor.js.src, function() {
        gulp.start('vendor-js');
    });

    // Recompile all vendor css
    watch(config.vendor.css.src, function() {
        gulp.start('vendor-css');
    });

    // Gather all other static from vendor
    watch(config.vendor.assets.src, function(){
        gulp.start('vendor-assets');
    });

    // JS with IE fixes
    watch(config.vendor.js.IEFixes.src, function(){
        gulp.start('ie-fixes');
    });
});

/**
 * Set the default command to run
 */
gulp.task('default', ['build'], function() {
    gulp.start('watch');
});
