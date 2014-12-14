

PIPELINE_CSS = {
    'metronic-core': {
        'source_filenames': (
            'metronic/plugins/bootstrap/css/bootstrap.css',
            'metronic/plugins/uniform/css/uniform.default.css',
        ),
        'output_filename': 'compiled/css/metronic-core.css',
    },
    'metronic-theme': {
        'source_filenames': (
            'metronic/css/style-metronic.css',
            'metronic/fonts/font.css',
            'metronic/css/style.css',
            'metronic/css/style-responsive.css',
            'metronic/css/plugins.css',
            'metronic/css/themes/default.css',
            'lily/css/custom.css',
        ),
        'output_filename': 'compiled/css/metronic-theme.css',
    },
    'print': {
        'source_filenames': (
            'metronic/css/print.css',
        ),
        'extra_context': {
            'media': 'print',
        },
        'output_filename': 'compiled/css/print.css',
    },
    'font-awesome': {
        'source_filenames': (
            'metronic/plugins/font-awesome/css/font-awesome.css',
        ),
        'output_filename': 'compiled/css/font-awesome.css',
    },
    'modal': {
        'source_filenames': (
            'metronic/plugins/bootstrap-modal/css/bootstrap-modal-bs3patch.css',
            'metronic/plugins/bootstrap-modal/css/bootstrap-modal.css',
        ),
        'output_filename': 'compiled/css/modal.css',
    },
    'tables': {
        'source_filenames': (
            'metronic/plugins/select2/select2_metro.css',
            'metronic/plugins/data-tables/DT_bootstrap.css',
        ),
        'output_filename': 'compiled/css/tables.css',
    },
    'notifications': {
        'source_filenames': (
            'metronic/plugins/bootstrap-toastr/toastr.min.css',
        ),
        'output_filename': 'compiled/css/notifications.css',
    },
    'forms': {
        'source_filenames': (
            'metronic/plugins/select2/select2_metro.css',
            'metronic/plugins/bootstrap-datepicker/css/datepicker.css',
            'metronic/plugins/bootstrap-datetimepicker/css/datetimepicker.css',
        ),
        'output_filename': 'compiled/css/forms.css',
    },
    'timeline': {
        'source_filenames': (
            'metronic/css/pages/timeline.css',
        ),
        'output_filename': 'compiled/css/timeline.css',
    },
    'tree': {
        'source_filenames': (
            'metronic/plugins/fuelux/css/tree-metronic.css',
        ),
        'output_filename': 'compiled/css/tree.css',
    },
    'wysihtml5': {  # Previously editor.css
        'source_filenames': (
            'metronic/plugins/bootstrap-wysihtml5/bootstrap-wysihtml5.css',
            'metronic/plugins/bootstrap-wysihtml5/wysiwyg-color.css',
        ),
        'output_filename': 'compiled/css/wysihtml5.css',
    },
    'wysihtml5-color': {  # Separately since wysihtml5 injects this in a generated iframe
        'source_filenames': (
            'metronic/plugins/bootstrap-wysihtml5/wysiwyg-color.css',
        ),
        'output_filename': 'compiled/css/wysihtml5-color.css',
    },
    'error': {
        'source_filenames': (
            'metronic/metronic/css/pages/error.css',
        ),
        'output_filename': 'compiled/css/error.css',
    },
    'blog': {
        'source_filenames': (
            'metronic/css/pages/blog.css',
        ),
        'output_filename': 'compiled/css/blog.css',
    },
    'login': {
        'source_filenames': (
            'metronic/css/pages/login.css',
            'metronic/css/pages/login-soft.css',
        ),
        'output_filename': 'compiled/css/login.css',
    },
    'news': {
        'source_filenames': (
            'metronic/css/pages/news.css',
        ),
        'output_filename': 'compiled/css/news.css',
    },
    'profile': {
        'source_filenames': (
            'metronic/css/pages/profile.css',
            'lily/css/profile.css',
        ),
        'output_filename': 'compiled/css/profile.css',
    },
    'cases': {
        'source_filenames': (
            'cases/css/cases.css',
        ),
        'output_filename': 'compiled/css/cases.css',
    },
    'deals': {
        'source_filenames': (
            'deals/css/deals.css',
        ),
        'output_filename': 'compiled/css/deals.css',
    },
    'inbox': {
        'source_filenames': (
            'metronic/css/pages/inbox.css',
            'email/css/inbox.css',
        ),
        'output_filename': 'compiled/css/inbox.css',
    },
}

PIPELINE_JS = {
    'jquery': {
        'source_filenames': (
            'metronic/plugins/jquery-1.10.2.min.js',
            'metronic/plugins/jquery-migrate-1.2.1.min.js',
            'metronic/plugins/jquery-ui/jquery-ui-1.10.3.custom.min.js',
        ),
        'output_filename': 'compiled/js/jquery.js',
    },
    'core': {
        'source_filenames': (
            'metronic/plugins/bootstrap/js/bootstrap.min.js',
            'metronic/plugins/bootstrap-hover-dropdown/twitter-bootstrap-hover-dropdown.min.js',
            'metronic/plugins/jquery-slimscroll/jquery.slimscroll.min.js',
            'metronic/plugins/jquery.blockui.min.js',
            'metronic/plugins/jquery.cookie.min.js',
            'metronic/plugins/uniform/jquery.uniform.min.js',
            'lily/scripts/gettext.js',
            'lily/scripts/forms/select2.js',
            'lily/plugins/jquery.truncate.js',
            'lily/plugins/content-toggle/jquery.contentToggle.js',
        ),
        'output_filename': 'compiled/js/core.js',
    },
    'ie9': {
        'source_filenames': (
            'metronic/plugins/respond.min.js',
            'metronic/plugins/excanvas.min.js',
        ),
        'output_filename': 'compiled/js/ie9.js',
    },
    'app': {
        'source_filenames': (
            'metronic/scripts/app.js',
            'lily/scripts/app.js',
            'lily/scripts/tasks.js',
        ),
        'output_filename': 'compiled/js/app.js',
    },
    'tables': {
        'source_filenames': (
            'metronic/plugins/select2/select2.js',
            'lily/plugins/data-tables/search-filter_diacritics.js',
            'lily/plugins/data-tables/jquery.dataTables.js',
            'lily/plugins/data-tables/column-sort_date-euro.js',
            'lily/plugins/data-tables/column-sort_date-uk.js',
            'lily/plugins/data-tables/column-sort_hidden-title-numeric.js',
            'metronic/plugins/data-tables/DT_bootstrap.js',
            'lily/scripts/list.js',
        ),
        'output_filename': 'compiled/js/tables.js',
    },
    'modal': {
        'source_filenames': (
            'metronic/plugins/bootstrap-modal/js/bootstrap-modalmanager.js',
            'metronic/plugins/bootstrap-modal/js/bootstrap-modal.js',
            'lily/scripts/modals/prevent_accidental_close.js',
            'lily/scripts/modals/prevent_stale_content.js',
        ),
        'output_filename': 'compiled/js/modal.js',
    },
    'ajax-submit': {
        'source_filenames': (
            'metronic/plugins/jquery-validation/lib/jquery.form.js',
        ),
        'output_filename': 'compiled/js/ajax-submit.js',
    },
    'notifications': {
        'source_filenames': (
            'metronic/plugins/bootstrap-toastr/toastr.js',
        ),
        'output_filename': 'compiled/js/notifications.js',
    },
    'forms': {
        'source_filenames': (
            'js/jquery.formset.js',
            'lily/scripts/forms/formset_init.js',
            'metronic/plugins/select2/select2.js',
            'metronic/plugins/bootstrap-datepicker/js/bootstrap-datepicker.js',
            'metronic/plugins/bootstrap-datetimepicker/js/bootstrap-datetimepicker.js',
            'provide/js/dataprovider.js',
            'utils/js/utils.js',
        ),
        'output_filename': 'compiled/js/forms.js',
    },
    'scroll': {
        'source_filenames': (
            'metronic/plugins/jquery-slimscroll/jquery.slimscroll.js',
        ),
        'output_filename': 'compiled/js/scroll.js',
    },
    'wysihtml5': {
        'source_filenames': (
            'lily/plugins/wysihtml5x/wysihtml5x.js',
            'lily/plugins/wysihtml5x/wysihtml5x-toolbar.js',
        ),
        'output_filename': 'compiled/js/wysihtml5.js',
    },
    'historylist': {
        'source_filenames': (
            'lily/scripts/historylist.js',
        ),
        'output_filename': 'compiled/js/historylist.js',
    },
    'cases': {
        'source_filenames': (
            'cases/js/cases.js',
        ),
        'output_filename': 'compiled/js/cases.js',
    },
    'deals': {
        'source_filenames': (
            'deals/js/deals.js',
        ),
        'output_filename': 'compiled/js/deals.js',
    },
    'inbox': {
        'source_filenames': (
            'email/js/inbox.js',
            'email/js/inbox-folders.js',
        ),
        'output_filename': 'compiled/js/inbox.js',
    },
    'emailtemplate': {
        'source_filenames': (
            'email/js/inbox.js',
            'email/js/emailtemplate.js',
        ),
        'output_filename': 'compiled/js/emailtemplate.js',
    },
    'password_strength': {
        'source_filenames': (
            'django_password_strength/js/zxcvbn.js',
            'django_password_strength/js/password_strength.js',
        ),
        'output_filename': 'compiled/js/password_strength.js',
    },
    'en_translations': {
        'source_filenames': (
            'jsi18n/en/djangojs.js',
        ),
        'output_filename': 'compiled/js/en-translations.js',
    },
    'nl_translations': {
        'source_filenames': (
            'jsi18n/nl/djangojs.js',
        ),
        'output_filename': 'compiled/js/nl-translations.js',
    },
    'angularapp': {
        'source_filenames': (
            'lily/angular/angular-1.3.5/angular.js',
            'lily/angular/angular-1.3.5/angular-cookies.js',
            'lily/angular/angular-bootstrap/ui-bootstrap-tpls-0.12.0.js',
            'lily/angular/app.js',
            'lily/angular/directives.js',
            'lily/angular/services.js',
            'lily/angular/accounts/services.js',
            'lily/angular/accounts/controllers.js',
            'lily/angular/contacts/services.js',
            'lily/angular/contacts/controllers.js',
        ),
        'output_filename': 'compiled/js/angularapp.js',
    },
}
