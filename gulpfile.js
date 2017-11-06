'use strict';

// Imports
var babel = require('gulp-babel');  // Transpiler for es6 syntax
var cached = require('gulp-cached');  // Only work on changed files
var cdnizer = require('gulp-cdnizer'); // Prepend CDN url to resources
var cleanhtml = require('gulp-cleanhtml');  // Strip whitespace eg.
var concat = require('gulp-concat');  // Merge file stream to one file
var del = require('del');  // Remove files/dirs
var ifElse = require('gulp-if-else');  // Conditional gulp steps
var gulp = require('gulp');  // Base module
var gutil = require('gulp-util');  // Various utils
var imagemin = require('gulp-imagemin');  // Minify/optimize images
var livereload = require('gulp-livereload');  // Live reload server (needs plugin install in Chrome)
var plumber = require('gulp-plumber');  // For error handling
var rebaseUrls = require('gulp-css-rebase-urls');  // Make relative paths absolute
var remember = require('gulp-remember');  // Remember all files after a cached call
var rename = require('gulp-rename');  // Rename current file stream
var sass = require('gulp-sass');  // Sass compilation
var shell = require('gulp-shell'); // For running shell commands
var size = require('gulp-size');  // Notify about filesize
var sourcemaps = require('gulp-sourcemaps');  // Create sourcemaps from original files and create a .map file
var templateCache = require('gulp-angular-templatecache');  // Create out of html files Angular templates in one js file/stream
var uglify = require('gulp-uglify');  // Minify javascript file
var uglifyCss = require('gulp-uglifycss');  // Minify css file
var watch = require('gulp-watch');  // Optimized file change watcher
var wrap = require('gulp-wrap');  // Surround current file(s) with other content (IIFE eg.)
var browserify = require('browserify');
var tap = require('gulp-tap');
var buffer = require('gulp-buffer');

/**
 * Config for Gulp.
 */
var config = {
    app: {
        buildDir: 'lily/static/app/',
        js: {
            src: [
                'frontend/app/**/module.js',
                'frontend/app/**/*.js',
                '!frontend/app/base/analytics.js',
            ],
            fileName: 'app.js',
            analytics: {
                src: [
                    'frontend/app/base/analytics.js',
                ],
                fileName: 'analytics.js',
            },
        },
        sass: {
            src: [
                'frontend/app/stylesheets/**/*.scss',
                '!frontend/app/stylesheets/login.scss',
            ],
            base: 'frontend/app/stylesheets/app.scss',
            fileName: 'app.css',
            login: {
                src: ['frontend/app/stylesheets/login.scss'],
                fileName: 'login.css',
            },
        },
        templates: {
            src: [
                'frontend/app/**/*.html',
            ],
            fileName: 'templates.js',
            module: 'app.templates',
        },
        assets: {
            src: [
                'frontend/app/**/*.*',
                '!frontend/app/**/*.css',
                '!frontend/app/**/*.scss',
                '!frontend/app/**/*.js',
                '!frontend/app/**/*.html',
            ],
        },
    },
    vendor: {
        buildDir: 'lily/static/vendor/',
        js: {
            src: [
                'frontend/vendor/**/*jquery.min.js',
                'frontend/vendor/**/*angular.js',
                'frontend/vendor/mousetrap.min.js',
                'frontend/vendor/**/*.js',
                '!frontend/vendor/**/angular-mocks.js',
            ],
            fileName: 'vendor.js',
        },
        css: {
            src: [
                'frontend/vendor/metronic/assets/global/plugins/bootstrap/css/bootstrap.css',
                'frontend/vendor/metronic/assets/global/plugins/select2/select2.css',
                'frontend/vendor/**/*.css',
            ],
            fileName: 'vendor.css',
        },
        assets: {
            src: [
                'frontend/vendor/**/*.*',
                '!frontend/vendor/**/*.css',
                '!frontend/vendor/**/*.scss',
                '!frontend/vendor/**/*.js',
                '!frontend/vendor/**/*.html',
            ],
        },
    },
    anonymousVendor: {
        buildDir: 'lily/static/vendor/',
        js: {
            src: [
                'frontend/vendor/**/*jquery.min.js',
                'frontend/vendor/**/hideShowPassword.min.js',
            ],
            fileName: 'anonymous_vendor.js',
        },
    },
    cdn: {
        defaultBase: (process.env.STATIC_URL || '/static/'),  // static url to prepend to all file paths.
        root: 'frontend/',
        src: [
            '**/*.{gif,png,jpg,jpeg,svg,ico}',  // Images
            '**/*.{eot,otf,ttf,woff,woff2}',  // Fonts with all types of crud on the back
            '**/*.{eot,otf,ttf,woff,woff2}?*',
            '**/*.{eot,otf,ttf,woff,woff2}#*',
            '**/*.{css,js}',  // Files
        ],
        images: {
            optimizationLevel: 3,
            multipass: true,
        },
    },
    heroku: {
        buildDir: 'lily/static/heroku/',
        assets: {
            src: ['frontend/app/heroku/*.*'],
        },
    },
    env: process.env.NODE_ENV || 'production',
};

var isProduction = (config.env === 'production');
var isWatcher = false;

var gulpSrc = gulp.src;
gulp.src = function() {
    return gulpSrc.apply(gulp, arguments)
        .pipe(plumber(function(error) {
            // Output an error message
            gutil.log(gutil.colors.red('Error (' + error.plugin + '): ' + error.message));
            // Emit the end event, to properly end the task.
            this.emit('end');
        }));
};

/**
 * Clean build dir.
 */
gulp.task('clean', [], function() {
    return del([
        'lily/static/',
    ]);
});

gulp.task('app-js', [], function(cb) {
    return gulp.src(config.app.js.src, {read: false})
        .pipe(tap(function(file) {
            // Replace file contents with browserify's bundle stream.
            file.contents = browserify(file.path, {debug: true}).bundle()
                .on('error', function(err) {
                    gutil.log(gutil.colors.red('Browserify error') + err);
                    gutil.beep();
                    cb();
                });
        }))
        // Transform streaming contents into buffer contents
        // (because gulp-sourcemaps does not support streaming contents).
        .pipe(buffer())
        .pipe(sourcemaps.init())
        .pipe(cached('app-js'))
        .pipe(babel({presets: ['env'], compact: false}))
        .pipe(wrap('(function(angular){\'use strict\';<%= contents %>})(angular);'))
        .pipe(ifElse(isProduction, uglify))
        .pipe(remember('app-js'))
        .pipe(concat(config.app.js.fileName))
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(config.app.buildDir))
        .pipe(ifElse(isWatcher, size))
        .pipe(ifElse(isWatcher, livereload));
});

gulp.task('app-css', [], function() {
    return gulp.src(config.app.sass.base)
        .pipe(sourcemaps.init())
        .pipe(sass({includePaths: ['./node_modules/']}))
        .pipe(rebaseUrls({root: config.cdn.root}))
        .pipe(cdnizer({
            defaultCDNBase: config.cdn.defaultBase,
            files: config.cdn.src,
        }))
        .pipe(ifElse(isProduction, uglifyCss))
        .pipe(rename(config.app.sass.fileName))
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(config.app.buildDir))
        .pipe(ifElse(isWatcher, size))
        .pipe(ifElse(isWatcher, livereload))
        .pipe(ifElse(!isProduction, function() {
            return shell(['styleguide']);
        }));
});

gulp.task('login-css', [], function() {
    return gulp.src(config.app.sass.login.src)
        .pipe(sourcemaps.init())
        .pipe(sass({includePaths: ['./node_modules/']}))
        .pipe(rebaseUrls({root: config.cdn.root}))
        .pipe(cdnizer({
            defaultCDNBase: config.cdn.defaultBase,
            files: config.cdn.src,
        }))
        .pipe(ifElse(isProduction, uglifyCss))
        .pipe(rename(config.app.sass.login.fileName))
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(config.app.buildDir))
        .pipe(ifElse(isWatcher, size))
        .pipe(ifElse(isWatcher, livereload));
});

/**
 * App templates.
 */
gulp.task('app-templates', [], function() {
    return gulp.src(config.app.templates.src)
        .pipe(cdnizer({
            defaultCDNBase: config.cdn.defaultBase,
            files: config.cdn.src,
        }))
        .pipe(cleanhtml())
        .pipe(templateCache(config.app.templates.fileName, {module: config.app.templates.module, standalone: true}))
        .pipe(wrap('(function(angular){\'use strict\';<%= contents %>})(angular);'))
        .pipe(ifElse(isProduction, uglify))
        .pipe(gulp.dest(config.app.buildDir))
        .pipe(ifElse(isWatcher, size))
        .pipe(ifElse(isWatcher, livereload));
});

gulp.task('app-assets', [], function() {
    return gulp.src(config.app.assets.src)
        .pipe(imagemin({
            optimizationLevel: config.cdn.images.optimizationLevel,
            multipass: config.cdn.images.multipass,
        }))
        .pipe(gulp.dest(config.app.buildDir))
        .pipe(ifElse(isWatcher, size))
        .pipe(ifElse(isWatcher, livereload));
});

/**
 * Concatenate and minify all vendor static.
 */
gulp.task('vendor-js', [], function() {
    return gulp.src(config.vendor.js.src)
        .pipe(sourcemaps.init())
        .pipe(cached('vendor-js'))
        .pipe(ifElse(isProduction, uglify))
        .pipe(remember('vendor-js'))
        .pipe(concat(config.vendor.js.fileName))
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(config.vendor.buildDir))
        .pipe(ifElse(isWatcher, size))
        .pipe(ifElse(isWatcher, livereload));
});

gulp.task('anonymous-vendor-js', [], function() {
    return gulp.src(config.anonymousVendor.js.src)
        .pipe(sourcemaps.init())
        .pipe(cached('anonymous-vendor-js'))
        .pipe(ifElse(isProduction, uglify))
        .pipe(remember('anonymous-vendor-js'))

        .pipe(concat(config.anonymousVendor.js.fileName))
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(config.anonymousVendor.buildDir))
        .pipe(ifElse(isWatcher, size))
        .pipe(ifElse(isWatcher, livereload));
});

gulp.task('vendor-css', [], function() {
    return gulp.src(config.vendor.css.src)
        .pipe(sourcemaps.init())
        .pipe(cached('vendor-css'))
        .pipe(rebaseUrls({root: config.cdn.root}))
        .pipe(cdnizer({
            defaultCDNBase: config.cdn.defaultBase,
            files: config.cdn.src,
        }))
        .pipe(ifElse(isProduction, uglifyCss))
        .pipe(remember('vendor-css'))

        .pipe(concat(config.vendor.css.fileName))
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(config.vendor.buildDir))
        .pipe(ifElse(isWatcher, size))
        .pipe(ifElse(isWatcher, livereload));
});

gulp.task('vendor-assets', [], function() {
    return gulp.src(config.vendor.assets.src)
        .pipe(imagemin({
            optimizationLevel: config.cdn.images.optimizationLevel,
            multipass: config.cdn.images.multipass,
        }))
        .pipe(gulp.dest(config.vendor.buildDir))
        .pipe(ifElse(isWatcher, size))
        .pipe(ifElse(isWatcher, livereload));
});

gulp.task('analytics', [], function() {
    // TODO: please remove this in the future
    return gulp.src(config.app.js.analytics.src)
        .pipe(rename(config.app.js.analytics.fileName))
        .pipe(gulp.dest(config.app.buildDir));
});

gulp.task('heroku-assets', [], function() {
    return gulp.src(config.heroku.assets.src)
        .pipe(gulp.dest(config.heroku.buildDir));
});

/**
 * Concatenate, minify and make source maps of all js and css.
 */
gulp.task('build', ['app-js', 'app-css', 'app-templates', 'app-assets', 'vendor-js', 'anonymous-vendor-js', 'vendor-css', 'vendor-assets',
    'analytics', 'heroku-assets', 'login-css'], function() {});

/**
 * Watch for changes
 */
gulp.task('watch', [], function() {
    isWatcher = true;
    livereload.listen();

    // Watch for changes in app javascript.
    watch(config.app.js.src, function() {
        gulp.start('app-js');
    });

    // Watch for changes in sass files.
    watch(config.app.sass.src, function() {
        gulp.start('app-css');
    });

    // Make our app templates.
    watch(config.app.templates.src, function() {
        gulp.start('app-templates');
    });

    // Gather all other static from the app.
    watch(config.app.assets.src, function() {
        gulp.start('app-assets');
    });

    // Watch google analytics script.
    watch(config.app.js.analytics.src, function() {
        gulp.start('analytics');
    });

    // Recompile all vendor js.
    watch(config.vendor.js.src, function() {
        gulp.start('vendor-js');
    });

    // Recompile all vendor css.
    watch(config.vendor.css.src, function() {
        gulp.start('vendor-css');
    });

    // Gather all other static from vendor.
    watch(config.vendor.assets.src, function() {
        gulp.start('vendor-assets');
    });
});

/**
 * Set the default command to run.
 */
gulp.task('default', ['build'], function() {
    gulp.start('watch');
});
