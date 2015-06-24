'use strict';

// Imports
var cdnizer = require('gulp-cdnizer'); // Prepend CDN url to resources
var cleanhtml = require('gulp-cleanhtml');  // strip whitespace eg.
var concat = require('gulp-concat');  // merge file stream to one file
var del = require('del');  // remove files/dirs
var gulp = require('gulp');  // base module
var fs = require('fs');  // File system
var livereload = require('gulp-livereload');  // live reload server (needs plugin install in Chrome)
var merge = require('merge-stream');  // Merge multiple gulp streams together
var path = require('path');  // File path helpers
var rename = require('gulp-rename');  // rename current file stream
var runSequence = require('run-sequence'); // Run tasks in sequence
var sass = require('gulp-sass');  // Sass compilation
var sourcemaps = require('gulp-sourcemaps');  // create sourcemaps from original files and create a .map file
var templateCache = require('gulp-angular-templatecache');  // create out of html files Angular templates in one js file/stream
var uglify = require('gulp-uglify');  // minify javascript file
var uglifyCss = require('gulp-uglifycss');  // minify css file
var watch = require('gulp-watch');
var wrap = require('gulp-wrap');  // surround current file(s) with other content (IIFE eg.)


/**
 * Config for Gulp
 */
var config = {
    app: {
        buildDir: 'lily/static/',
        js: {
            modules: {
                basepath: 'frontend/app/',
                buildDir: 'lily/static/modules/',
                src: [
                    '**/module.js',
                    '**/*.js'
                ]
            },
            src: [
                'lily/static/modules/*.js'  // Should match build dir of modules
            ],
            fileName: 'app.js'
        },
        sass: {
            src: 'frontend/app/app.scss',
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
                'frontend/vendor/**/*.js'
            ],
            fileName: 'vendor.js'
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
        defaultBase: "/static/",  // static for local cloudfront url for live.
        src: {
            imgs: '**/*.{gif,png,jpg,jpeg,svg,ico}',  // Images/graphics
            fonts: '**/*.{eot,otf,ttf,woff,woff2}',  // Fonts
            files: '**/*.{css,js}'  // Files
        }
    }
};

/**
 * Helper functions for gulp
 */
function getFolders(dir) {
    return fs.readdirSync(dir).filter(function(file) {
        return fs.statSync(path.join(dir, file)).isDirectory();
    });
}

function getJsModuleSrc(folder) {
    var moduleSrc = [];
    folder = (folder !== "undefined") ? folder : '';
    for (var i in config.app.js.modules.src) {
        moduleSrc.push(path.join(config.app.js.modules.basepath, folder, config.app.js.modules.src[i]));
    }
    return moduleSrc;
}

function buildJsModule(folder) {
    // make array with filepaths (module.js first)
    var moduleSrc = getJsModuleSrc(folder);

    return gulp.src(moduleSrc)
        // Create source map
        .pipe(sourcemaps.init())
        // Wrap in IIFE
        .pipe(wrap('(function(angular){\n\'use strict\';\n<%= contents %>\n})(angular);'))
        // Concatenate into foldername.min.js
        .pipe(concat(folder + '.js'))
        // Minify
        .pipe(uglify())
        // Write to output (both the source and sourcemap)
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(config.app.js.modules.buildDir));
}

/**
 * Clean build dir
 */
gulp.task('clean', [], function() {
    return del([
        'lily/static/'
    ]);
});

/**
 * Concatenate and minify all app js per module (folder)
 */
gulp.task('app-js-modules', [], function() {
    var folders = getFolders(config.app.js.modules.basepath);

    var modules = folders.map(function(folder) {
        return buildJsModule(folder);
    });

    return merge(modules);
});

/**
 * Concatenate all modules into a single app js
 */
gulp.task('app-js', [], function() {
    return gulp.src(config.app.js.src)
        .pipe(sourcemaps.init({loadMaps: true}))
        .pipe(concat(config.app.js.fileName))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(config.app.buildDir))
        .pipe(livereload());
});

gulp.task('app-css', [], function() {
    return gulp.src(config.app.sass.src)
        .pipe(sass().on('error', sass.logError))
        .pipe(cdnizer({
            defaultCDNBase: config.cdn.defaultBase,
            files: [
                config.cdn.src.imgs,
                config.cdn.src.fonts
            ]
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
            files: [
                config.cdn.src.imgs,
                config.cdn.src.files
            ]
        }))
        .pipe(cleanhtml())
        .pipe(templateCache(config.app.templates.fileName, {module: config.app.templates.module, standalone:true}))
        .pipe(wrap('(function(angular){\n\'use strict\';\n<%= contents %>\n})(angular);'))
        .pipe(uglify())
        .pipe(gulp.dest(config.app.buildDir))
        .pipe(livereload());
});

gulp.task('app-assets', [], function(){
    return gulp.src(config.app.assets.src)
        .pipe(gulp.dest(config.app.buildDir))
        .pipe(livereload());
});

/**
 * Concatenate and minify all vendor static
 */
gulp.task('vendor-js', [], function() {
    return gulp.src(config.vendor.js.src)
        .pipe(sourcemaps.init())
        .pipe(concat(config.vendor.js.fileName))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(config.vendor.buildDir))
        .pipe(livereload());
});

gulp.task('vendor-css', [], function() {
    return gulp.src(config.vendor.css.src)
        .pipe(sourcemaps.init())
        .pipe(cdnizer({
            defaultCDNBase: config.cdn.defaultBase,
            files: [
                config.cdn.src.fonts,
                config.cdn.src.imgs,
                config.cdn.src.files
            ],
            relativeRoot: 'vendor/'
        }))
        .pipe(concat(config.vendor.css.fileName))
        .pipe(uglifyCss())
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(config.vendor.buildDir))
        .pipe(livereload());
});

gulp.task('vendor-assets', [], function() {
    return gulp.src(config.vendor.assets.src)
        .pipe(gulp.dest(config.vendor.buildDir))
        .pipe(livereload());
});

/**
 * Concatenate, minify and make source maps of all js and css
 */
gulp.task('build', [], function() {
    runSequence(
        'app-js-modules',  // Because of app-js this needs to run first
        ['app-js', 'app-css', 'app-templates', 'app-assets', 'vendor-js', 'vendor-css', 'vendor-assets']
    );
});

/**
 * Watch for changes
 */
gulp.task('watch', [], function() {
    // Watch for js module changes
    watch(config.app.js.modules.basepath + '**/*.js', function(vinyl) {
        var modules = vinyl.history.map(function(path) {
            var basepath = config.app.js.modules.basepath;

            var folder = path.slice(path.search(basepath) + basepath.length);
            folder = folder.slice(0, folder.search('/'));

            console.log('Recompiling ' + folder + '.js');

            return buildJsModule(folder)
        });

        console.log('Done recompiling');

        return merge(modules)
    });

    // Watch for js changes in any of the modules
    watch(config.app.js.modules.buildDir + '**/*.js', function() {
        gulp.start('app-js');
    });

    // Watch for changes in sass files
    watch('frontend/app/**/*.scss', function() {
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
});

/**
 * Set the default command to run
 */
gulp.task('default', ['build'], function() {

});
