
PIPELINE_CSS = {
    'anonymous': {
        'source_filenames': (
            'metronic/assets/global/plugins/font-awesome/css/font-awesome.css',
            'metronic/assets/global/plugins/simple-line-icons/simple-line-icons.css',
            'metronic/assets/global/plugins/bootstrap/css/bootstrap.css',
            'metronic/assets/global/plugins/uniform/css/uniform.default.css',
            'metronic/assets/global/plugins/bootstrap-toastr/toastr.css',
            'metronic/assets/global/css/components-rounded.css',
            'metronic/assets/global/css/plugins.css',
            'metronic/assets/admin/layout4/css/layout.css',
            'metronic/assets/admin/layout4/css/themes/light.css',
            'users/css/custom.css',
        ),
        'output_filename': 'metronic/css/anonymous_global.css',
    },
    'vendor': {
        'source_filenames': (
            'build/vendor.min.css',
        ),
        'output_filename': 'compiled/css/vendor.css',
    },
    'app': {
        'source_filenames': (
            'build/app.min.css',
        ),
        'output_filename': 'compiled/css/app.css',
    },
}

PIPELINE_JS = {
    'anonymous': {
        'source_filenames': (
            'metronic/assets/global/plugins/jquery.min.js',
            'metronic/assets/global/plugins/jquery-migrate.min.js',
            'metronic/assets/global/plugins/jquery-ui/jquery-ui.min.js',

            'metronic/assets/global/plugins/bootstrap/js/bootstrap.min.js',
            'metronic/assets/global/plugins/bootstrap-toastr/toastr.js',
            'lily/plugins/analytics/analytics.js',

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

            'cases/js/angular/controllers.js',
            'cases/js/angular/directives.js',
            'cases/js/angular/assignto.ctrl.js',
            'cases/js/angular/postpone.ctrl.js',
            'cases/js/angular/services.js',
            'cases/js/cases.js',

            'contacts/js/angular/controllers.js',
            'contacts/js/angular/services.js',
            'contacts/js/angular/directives/module.js',
            'contacts/js/angular/directives/list_widget.js',
            'contacts/js/angular/directives/detail_widget.js',

            'dashboard/js/angular/controllers/module.js',
            'dashboard/js/angular/controllers/base.js',
            'dashboard/js/angular/directives/module.js',
            'dashboard/js/angular/directives/callback.js',
            'dashboard/js/angular/directives/dealstocheck.js',
            'dashboard/js/angular/directives/feedback.js',
            'dashboard/js/angular/directives/mycases.js',
            'dashboard/js/angular/directives/queuesize.js',
            'dashboard/js/angular/directives/teams.js',
            'dashboard/js/angular/directives/unassigned.js',
            'dashboard/js/angular/directives/unread.js',
            'dashboard/js/angular/directives/followup.js',

            'deals/js/angular/controllers.js',
            'deals/js/angular/followup_widget_ctrl.js',
            'deals/js/angular/services.js',
            'deals/js/angular/directives/module.js',
            'deals/js/angular/directives/list_widget.js',

            'email/js/angular/module.js',
            'email/js/angular/base.ctrl.js',
            'email/js/angular/email.compose.ctrl.js',
            'email/js/angular/email.detail.ctrl.js',
            'email/js/angular/email.list.ctrl.js',
            'email/js/angular/directives.js',
            'email/js/angular/services.js',
            'email/js/inbox.js',
            'email/js/emailtemplate.js',

            'notes/js/angular/services.js',

            'preferences/js/angular/module.js',
            'preferences/js/angular/base.ctrl.js',
            'preferences/js/angular/email/module.js',
            'preferences/js/angular/email/controllers.js',
            'preferences/js/angular/email/emailaccountlist.controller.js',
            'preferences/js/angular/user/module.js',
            'preferences/js/angular/user/controllers/api_token.js',
            'preferences/js/angular/user/controllers/base.js',
            'preferences/js/angular/user/controllers/user_account.js',
            'preferences/js/angular/user/controllers/user_profile.js',

            'users/js/angular/services.js',
            'users/js/angular/filters.js',

            'utils/js/angular/controllers.js',
            'utils/js/angular/directives.js',

            # Pip package static
            'js/jquery.formset.js',
            'django_password_strength/js/zxcvbn.js',
            'django_password_strength/js/password_strength.js',
        ),
        'output_filename': 'compiled/js/global.js',
    },
    'vendor': {
        'source_filenames': (
            'build/vendor.min.js',
        ),
        'output_filename': 'compiled/js/vendor.js',
    },
    'app': {
        'source_filenames': (
            'build/app.min.js',
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
