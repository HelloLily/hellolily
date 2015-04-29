
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
            'metronic/assets/admin/pages/css/profile-old.css',  # TODO: LILY-824: Remove this after history list update
            'metronic/assets/admin/pages/css/profile.css',
            'metronic/assets/admin/layout4/css/layout.css',
            'metronic/assets/admin/layout4/css/themes/light.css',
            'metronic/assets/global/css/components-rounded.css',
            'metronic/assets/global/css/plugins.css',
            'metronic/assets/global/plugins/bootstrap-wysihtml5/bootstrap-wysihtml5.css',
            'metronic/assets/global/plugins/bootstrap-wysihtml5/wysiwyg-color.css',

            'plugins/angular/angular-chart/angular-chart.css',

            # Custom timeline
            'lily/css/custom.css',

            'lily/css/profile.css',  # TODO: LILY-824: Remove this after history list update
            'accounts/css/accounts.css',  # TODO: LILY-824: Remove this after history list update
            'email/css/inbox.css',
        ),
        'output_filename': 'metronic/css/global.css',
    },
}

PIPELINE_JS = {
    'global-ie': {
        'source_filenames': (
            'metronic/assets/global/plugins/respond.js',
            'metronic/assets/global/plugins/excanvas.js',
        ),
        'output_filename': 'compiled/js/global-ie.js',
    },
    'global': {
        'source_filenames': (
            'metronic/assets/global/plugins/jquery.min.js',
            'metronic/assets/global/plugins/jquery-migrate.min.js',
            # Load jquery-ui.min.js before bootstrap.min.js to fix bootstrap tooltip conflict with jquery ui tooltip
            'metronic/assets/global/plugins/jquery-ui/jquery-ui.min.js',
            'metronic/assets/global/plugins/bootstrap/js/bootstrap.min.js',
            'metronic/assets/global/plugins/bootstrap-hover-dropdown/bootstrap-hover-dropdown.min.js',
            'metronic/assets/global/plugins/jquery-slimscroll/jquery.slimscroll.js',  # Upgrade to new version without custom patch as soon as PR 198 gets through
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
            'plugins/diff.js',

            # Angular base
            'plugins/angular/angular.js',
            'plugins/angular/angular-cookies.js',
            'plugins/angular/angular-resource.js',

            # Angular plugins
            'plugins/angular/angular-bootstrap/ui-bootstrap-tpls-0.12.1.js',
            'plugins/angular/angular-breadcrumb/angular-breadcrumb.js',
            'plugins/chart.js',
            'plugins/angular/angular-angulartics/angulartics.js',
            'plugins/angular/angular-angulartics/angulartics-ga.js',
            'plugins/angular/angular-chart/angular-chart.js',
            'plugins/angular/angular-sanitize/angular-sanitize.js',
            'plugins/angular/angular-slimscroll/angular-slimscroll.js',
            'plugins/angular/angular-ui-router/angular-ui-router.js',

            # Angular Lily app
            'lily/js/angular/app.js',
            'lily/js/angular/controllers.js',
            'lily/js/angular/directives.js',
            'lily/js/angular/filters.js',
            'lily/js/angular/services.js',

            'accounts/js/angular/controllers.js',
            'accounts/js/angular/services.js',

            'cases/js/angular/controllers.js',
            'cases/js/angular/directives.js',
            'cases/js/angular/services.js',
            'cases/js/cases.js',

            'contacts/js/angular/controllers.js',
            'contacts/js/angular/services.js',

            'dashboard/js/angular/module.js',
            'dashboard/js/angular/base.ctrl.js',
            'dashboard/js/angular/directives.js',

            'deals/js/angular/controllers.js',
            'deals/js/angular/services.js',

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
            'preferences/js/angular/user/controllers.js',

            'users/js/angular/services.js',
            'users/js/angular/filters.js',

            'utils/js/angular/controllers.js',

            # Pip package static
            'js/jquery.formset.js',
            'django_password_strength/js/zxcvbn.js',
            'django_password_strength/js/password_strength.js',

            # Our JavaScript
            'lily/js/forms/formsets.js',
            'lily/js/forms/select2.js',
            'lily/js/forms/show-and-hide.js',
            'utils/js/utils.js',
            'provide/js/dataprovider.js',
        ),
        'output_filename': 'compiled/js/global.js',
    },
}
