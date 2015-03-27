
PIPELINE_CSS = {
    'global': {
        'source_filenames': (
            # Metronic global
            'metronic/assets/global/plugins/font-awesome/css/font-awesome.css',
            'metronic/assets/global/plugins/simple-line-icons/simple-line-icons.css',
            'metronic/assets/global/plugins/bootstrap/css/bootstrap.css',
            'metronic/assets/global/plugins/uniform/css/uniform.default.css',
            'metronic/assets/global/plugins/bootstrap-switch/css/bootstrap-switch.css',
            'metronic/assets/global/plugins/bootstrap-toastr/toastr.css',
            'metronic/assets/global/plugins/select2/select2.css',

            # Metronic layout
            'metronic/assets/admin/pages/css/inbox.css',
            'metronic/assets/admin/pages/css/profile-old.css',  # deze sheit moet er uit na history list update
            'metronic/assets/admin/layout4/css/layout.css',
            'metronic/assets/admin/layout4/css/themes/light.css',
            'metronic/assets/global/css/components-rounded.css',
            'metronic/assets/global/css/plugins.css',
            'metronic/assets/global/plugins/bootstrap-wysihtml5/bootstrap-wysihtml5.css',
            'metronic/assets/global/plugins/bootstrap-wysihtml5/wysiwyg-color.css',

            'plugins/angular/angular-chart/angular-chart.css',

            # Custom timeline
            'lily/sass/custom.css',

            'lily/css/profile.css',
            'accounts/css/accounts.css',
            'email/css/inbox.css',
        ),
        'output_filename': 'metronic/css/global.css',
    },
    # 'base': {
    #     'source_filenames': (
    #         'metronic/css/style-metronic.css',
    #         'metronic/fonts/font.css',
    #         'metronic/css/style.css',
    #         'metronic/css/layout.css',
    #         'metronic/css/style-responsive.css',
    #         'metronic/css/plugins.css',
    #         'metronic/css/themes/default.css',
    #         'metronic/plugins/bootstrap/css/bootstrap.css',
    #         'metronic/plugins/uniform/css/uniform.default.css',
    #         'metronic/plugins/font-awesome/css/font-awesome.css',
    #         'metronic/plugins/font-awesome/css/font-awesome.css',
    #         'lily/css/custom.css',
    #     ),
    #     'output_filename': 'compiled/css/base.css',
    # },
    # 'print': {
    #     'source_filenames': (
    #         'metronic/css/print.css',
    #     ),
    #     'extra_context': {
    #         'media': 'print',
    #     },
    #     'output_filename': 'compiled/css/print.css',
    # },
    # 'modal': {
    #     'source_filenames': (
    #         'metronic/plugins/bootstrap-modal/css/bootstrap-modal-bs3patch.css',
    #         'metronic/plugins/bootstrap-modal/css/bootstrap-modal.css',
    #     ),
    #     'output_filename': 'compiled/css/modal.css',
    # },
    # 'tables': {
    #     'source_filenames': (
    #         'metronic/plugins/select2/select2_metro.css',
    #         'metronic/plugins/data-tables/DT_bootstrap.css',
    #     ),
    #     'output_filename': 'compiled/css/tables.css',
    # },
    # 'notifications': {
    #     'source_filenames': (
    #         'metronic/plugins/bootstrap-toastr/toastr.min.css',
    #     ),
    #     'output_filename': 'compiled/css/notifications.css',
    # },
    # 'forms': {
    #     'source_filenames': (
    #         'metronic/plugins/select2/select2_metro.css',
    #         'metronic/plugins/bootstrap-datepicker/css/datepicker.css',
    #         'metronic/plugins/bootstrap-datetimepicker/css/datetimepicker.css',
    #     ),
    #     'output_filename': 'compiled/css/forms.css',
    # },
    # 'timeline': {
    #     'source_filenames': (
    #         'metronic/css/pages/timeline.css',
    #     ),
    #     'output_filename': 'compiled/css/timeline.css',
    # },
    # 'tree': {
    #     'source_filenames': (
    #         'metronic/plugins/fuelux/css/tree-metronic.css',
    #     ),
    #     'output_filename': 'compiled/css/tree.css',
    # },
    # 'wysihtml5': {  # Previously editor.css
    #     'source_filenames': (
    #         'metronic/plugins/bootstrap-wysihtml5/bootstrap-wysihtml5.css',
    #         'metronic/plugins/bootstrap-wysihtml5/wysiwyg-color.css',
    #     ),
    #     'output_filename': 'compiled/css/wysihtml5.css',
    # },
    # 'wysihtml5-color': {  # Separately since wysihtml5 injects this in a generated iframe
    #     'source_filenames': (
    #         'metronic/plugins/bootstrap-wysihtml5/wysiwyg-color.css',
    #     ),
    #     'output_filename': 'compiled/css/wysihtml5-color.css',
    # },
    # 'error': {
    #     'source_filenames': (
    #         'metronic/metronic/css/pages/error.css',
    #     ),
    #     'output_filename': 'compiled/css/error.css',
    # },
    # 'blog': {
    #     'source_filenames': (
    #         'metronic/css/pages/blog.css',
    #     ),
    #     'output_filename': 'compiled/css/blog.css',
    # },
    # 'login': {
    #     'source_filenames': (
    #         'metronic/css/pages/login.css',
    #         'metronic/css/pages/login-soft.css',
    #     ),
    #     'output_filename': 'compiled/css/login.css',
    # },
    # 'news': {
    #     'source_filenames': (
    #         'metronic/css/pages/news.css',
    #     ),
    #     'output_filename': 'compiled/css/news.css',
    # },
    # 'profile': {
    #     'source_filenames': (
    #         'metronic/css/pages/profile.css',
    #         'lily/css/profile.css',
    #     ),
    #     'output_filename': 'compiled/css/profile.css',
    # },
    # 'cases': {
    #     'source_filenames': (
    #         'cases/css/cases.css',
    #     ),
    #     'output_filename': 'compiled/css/cases.css',
    # },
    # 'deals': {
    #     'source_filenames': (
    #         'deals/css/deals.css',
    #     ),
    #     'output_filename': 'compiled/css/deals.css',
    # },
    # 'inbox': {
    #     'source_filenames': (
    #         'metronic/css/pages/inbox.css',
    #         'email/css/inbox.css',
    #     ),
    #     'output_filename': 'compiled/css/inbox.css',
    # },
    # 'accounts': {
    #     'source_filenames': (
    #         'accounts/css/accounts.css',
    #     ),
    #     'output_filename': 'compiled/css/accounts.css',
    # },
    # 'contacts': {
    #     'source_filenames': (
    #         'contacts/css/contacts.css',
    #     ),
    #     'output_filename': 'compiled/css/contacts.css',
    # },
}

PIPELINE_JS = {
    'global-ie': {
        'source_filenames': (
            'metronic/assets/global/plugins/respond.js',
            'metronic/assets/global/plugins/excanvas.js',
        ),
        'output_filename': 'compiled/js/global.js',
    },
    'global': {
        'source_filenames': (
            'metronic/assets/global/plugins/jquery.min.js',
            'metronic/assets/global/plugins/jquery-migrate.min.js',
            # Load jquery-ui.min.js before bootstrap.min.js to fix bootstrap tooltip conflict with jquery ui tooltip
            'metronic/assets/global/plugins/jquery-ui/jquery-ui.min.js',
            'metronic/assets/global/plugins/bootstrap/js/bootstrap.min.js',
            'metronic/assets/global/plugins/bootstrap-hover-dropdown/bootstrap-hover-dropdown.min.js',
            'metronic/assets/global/plugins/jquery-slimscroll/jquery.slimscroll.min.js',
            'metronic/assets/global/plugins/jquery.blockui.min.js',
            'metronic/assets/global/plugins/jquery.cokie.min.js',
            # 'metronic/assets/global/plugins/uniform/jquery.uniform.js',
            'metronic/assets/global/plugins/bootstrap-switch/js/bootstrap-switch.min.js',
            'metronic/assets/global/plugins/bootstrap-datepicker/js/bootstrap-datepicker.js',
            'metronic/assets/global/plugins/bootstrap-datetimepicker/js/bootstrap-datetimepicker.js',
            'metronic/assets/global/plugins/bootstrap-toastr/toastr.js',
            'metronic/assets/global/plugins/select2/select2.js',
            'metronic/assets/global/scripts/metronic.js',
            'metronic/assets/admin/layout4/scripts/layout.js',
            'metronic/assets/admin/layout4/scripts/demo.js',
            'lily/plugins/wysihtml/wysihtml.js',
            'lily/plugins/wysihtml/wysihtml-toolbar.js',

            # Angular base
            'plugins/angular/angular.js',
            'plugins/angular/angular-cookies.js',
            'plugins/angular/angular-resource.js',

            # Angular Plugins
            'plugins/angular/angular-bootstrap/ui-bootstrap-tpls-0.12.0.js',
            'plugins/angular/angular-breadcrumb/angular-breadcrumb.js',
            'plugins/chart.js',
            'plugins/angular/angular-chart/angular-chart.js',
            'plugins/angular/angular-sanitize/angular-sanitize.js',
            'plugins/angular/angular-slimscroll/angular-slimscroll.js',
            'plugins/angular/angular-ui-router/angular-ui-router.js',

            # Angular lily app
            'lily/js/angular/app.js',
            'lily/js/angular/controllers.js',
            'lily/js/angular/directives.js',
            'lily/js/angular/filters.js',
            'lily/js/angular/services.js',

            'accounts/js/angular/controllers.js',
            'accounts/js/angular/services.js',

            'cases/js/angular/controllers.js',
            'cases/js/angular/services.js',
            'cases/js/cases.js',

            'contacts/js/angular/controllers.js',
            'contacts/js/angular/services.js',

            'dashboard/js/angular/controllers.js',
            'dashboard/js/angular/directives.js',

            'deals/js/angular/controllers.js',
            'deals/js/angular/services.js',

            'email/js/angular/controllers.js',
            'email/js/angular/services.js',
            'email/js/inbox.js',

            'notes/js/angular/services.js',

            'users/js/angular/services.js',
            'users/js/angular/filters.js',

            'utils/js/angular/controllers.js',

            # Pip package static
            'js/jquery.formset.js',

            # Stuffz
            'lily/js/forms/formsets.js',
            'lily/js/forms/select2.js',
            'lily/js/forms/show-and-hide.js',
            'provide/js/dataprovider.js',
        ),
        'output_filename': 'compiled/js/global.js',
    },
    # 'jquery': {
    #     'source_filenames': (
    #         'metronic/plugins/jquery-1.10.2.min.js',
    #         'metronic/plugins/jquery-migrate-1.2.1.min.js',
    #         'metronic/plugins/jquery-ui/jquery-ui-1.10.3.custom.min.js',
    #     ),
    #     'output_filename': 'compiled/js/jquery.js',
    # },
    # 'core': {
    #     'source_filenames': (
    #         'metronic/plugins/bootstrap/js/bootstrap.min.js',
    #         'metronic/plugins/bootstrap-hover-dropdown/twitter-bootstrap-hover-dropdown.min.js',
    #         'metronic/plugins/jquery-slimscroll/jquery.slimscroll.min.js',
    #         'metronic/plugins/jquery.blockui.min.js',
    #         'metronic/plugins/jquery.cookie.min.js',
    #         'metronic/plugins/uniform/jquery.uniform.min.js',
    #         'lily/scripts/gettext.js',
    #         'lily/scripts/forms/select2.js',
    #         'lily/plugins/jquery.truncate.js',
    #         'lily/plugins/content-toggle/jquery.contentToggle.js',
    #     ),
    #     'output_filename': 'compiled/js/core.js',
    # },
    # 'ie9': {
    #     'source_filenames': (
    #         'metronic/plugins/respond.min.js',
    #         'metronic/plugins/excanvas.min.js',
    #     ),
    #     'output_filename': 'compiled/js/ie9.js',
    # },
    # 'app': {
    #     'source_filenames': (
    #         'metronic/scripts/app.js',
    #         'lily/scripts/app.js',
    #         'lily/scripts/tasks.js',
    #     ),
    #     'output_filename': 'compiled/js/app.js',
    # },
    # 'tables': {
    #     'source_filenames': (
    #         'metronic/plugins/select2/select2.js',
    #         'lily/plugins/data-tables/search-filter_diacritics.js',
    #         'lily/plugins/data-tables/jquery.dataTables.js',
    #         'lily/plugins/data-tables/column-sort_date-euro.js',
    #         'lily/plugins/data-tables/column-sort_date-uk.js',
    #         'lily/plugins/data-tables/column-sort_hidden-title-numeric.js',
    #         'metronic/plugins/data-tables/DT_bootstrap.js',
    #         'lily/scripts/list.js',
    #     ),
    #     'output_filename': 'compiled/js/tables.js',
    # },
    # 'modal': {
    #     'source_filenames': (
    #         'metronic/plugins/bootstrap-modal/js/bootstrap-modalmanager.js',
    #         'metronic/plugins/bootstrap-modal/js/bootstrap-modal.js',
    #         'lily/scripts/modals/prevent_accidental_close.js',
    #         'lily/scripts/modals/prevent_stale_content.js',
    #     ),
    #     'output_filename': 'compiled/js/modal.js',
    # },
    # 'ajax-submit': {
    #     'source_filenames': (
    #         'metronic/plugins/jquery-validation/lib/jquery.form.js',
    #     ),
    #     'output_filename': 'compiled/js/ajax-submit.js',
    # },
    # 'notifications': {
    #     'source_filenames': (
    #         'metronic/plugins/bootstrap-toastr/toastr.js',
    #     ),
    #     'output_filename': 'compiled/js/notifications.js',
    # },
    # 'forms': {
    #     'source_filenames': (
    #         'js/jquery.formset.js',
    #         'lily/scripts/forms/formset_init.js',
    #         'metronic/plugins/select2/select2.js',
    #         'metronic/plugins/bootstrap-datepicker/js/bootstrap-datepicker.js',
    #         'metronic/plugins/bootstrap-datetimepicker/js/bootstrap-datetimepicker.js',
    #         'provide/js/dataprovider.js',
    #         'utils/js/utils.js',
    #     ),
    #     'output_filename': 'compiled/js/forms.js',
    # },
    # 'scroll': {
    #     'source_filenames': (
    #         'metronic/plugins/jquery-slimscroll/jquery.slimscroll.js',
    #     ),
    #     'output_filename': 'compiled/js/scroll.js',
    # },
    # 'wysihtml5': {
    #     'source_filenames': (
    #         'lily/plugins/wysihtml/wysihtml.js',
    #         'lily/plugins/wysihtml/wysihtml-toolbar.js',
    #     ),
    #     'output_filename': 'compiled/js/wysihtml5.js',
    # },
    # 'historylist': {
    #     'source_filenames': (
    #         'lily/scripts/historylist.js',
    #     ),
    #     'output_filename': 'compiled/js/historylist.js',
    # },
    # 'cases': {
    #     'source_filenames': (
    #         'cases/js/cases.js',
    #     ),
    #     'output_filename': 'compiled/js/cases.js',
    # },
    # 'deals': {
    #     'source_filenames': (
    #         'deals/js/deals.js',
    #     ),
    #     'output_filename': 'compiled/js/deals.js',
    # },
    # 'inbox': {
    #     'source_filenames': (
    #         'email/js/inbox.js',
    #         'email/js/inbox-folders.js',
    #     ),
    #     'output_filename': 'compiled/js/inbox.js',
    # },
    # 'emailtemplate': {
    #     'source_filenames': (
    #         'email/js/inbox.js',
    #         'email/js/emailtemplate.js',
    #     ),
    #     'output_filename': 'compiled/js/emailtemplate.js',
    # },
    # 'password_strength': {
    #     'source_filenames': (
    #         'django_password_strength/js/zxcvbn.js',
    #         'django_password_strength/js/password_strength.js',
    #     ),
    #     'output_filename': 'compiled/js/password_strength.js',
    # },
    # 'en_translations': {
    #     'source_filenames': (
    #         'jsi18n/en/djangojs.js',
    #     ),
    #     'output_filename': 'compiled/js/en-translations.js',
    # },
    # 'nl_translations': {
    #     'source_filenames': (
    #         'jsi18n/nl/djangojs.js',
    #     ),
    #     'output_filename': 'compiled/js/nl-translations.js',
    # },
    # 'angularapp': {
    #     'source_filenames': (
    #         'lily/angular/angular-1.3.5/angular.js',
    #         'lily/angular/angular-1.3.5/angular-resource.js',
    #         'lily/angular/angular-1.3.5/angular-cookies.js',
    #         'lily/angular/angular-1.3.5/angular-resource.js',
    #         'lily/angular/angular-bootstrap/ui-bootstrap-tpls-0.12.0.js',
    #         'lily/angular/angular-ui-router/angular-ui-router.js',
    #         'lily/angular/app.js',
    #         'lily/angular/directives.js',
    #         'lily/angular/filters.js',
    #         'lily/angular/services.js',
    #         'lily/angular/accounts/services.js',
    #         'lily/angular/accounts/controllers.js',
    #         'lily/angular/cases/services.js',
    #         'lily/angular/cases/controllers.js',
    #         'lily/angular/contacts/services.js',
    #         'lily/angular/contacts/controllers.js',
    #         'lily/angular/deals/services.js',
    #         'lily/angular/deals/controllers.js',
    #         'lily/angular/email/services.js',
    #         'lily/angular/email/controllers.js',
    #         'lily/angular/notes/services.js',
    #     ),
    #     'output_filename': 'compiled/js/angularapp.js',
    # },
}
