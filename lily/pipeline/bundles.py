PIPELINE_JS = {
    'anonymous': {
        'source_filenames': (
            'vendor/vendor.js',

            # Lily static
            'analytics.js',

            # Pip package static
            'django_password_strength/js/zxcvbn.js',
            'django_password_strength/js/password_strength.js',
        ),
        'output_filename': 'compiled/js/anonymous.js'
    },
    'global-ie': {
        'source_filenames': (
            'metronic/assets/global/plugins/respond.js',
            'metronic/assets/global/plugins/excanvas.js',
        ),
        'output_filename': 'compiled/js/global-ie.js',
    },
    'global': {
        'source_filenames': (
            'users/js/angular/services.js',
            'users/js/angular/filters.js',

            # Pip package static
            # 'js/jquery.formset.js',
            'django_password_strength/js/zxcvbn.js',
            'django_password_strength/js/password_strength.js',
        ),
        'output_filename': 'compiled/js/global.js',
    },
    'vendor': {
        'source_filenames': (
            'build/vendor.js',
        ),
        'output_filename': 'compiled/js/vendor.js',
    },
    'app': {
        'source_filenames': (
            'build/app.js',
        ),
        'output_filename': 'compiled/js/app.js',
    },
    'templates': {
        'source_filenames': (
            'build/templates.js',
        ),
        'output_filename': 'compiled/js/templates.js',
    },
}
