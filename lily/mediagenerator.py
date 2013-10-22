# used jquery css
jquery_bundle_css = (
    'mwsadmin/jui/css/jquery.ui.core.css',
    'mwsadmin/jui/css/jquery.ui.resizable.css',
    # 'mwsadmin/jui/css/jquery.ui.accordion.css',
    'mwsadmin/jui/css/jquery.ui.autocomplete.css',
    'mwsadmin/jui/css/jquery.ui.dialog.css',
    # 'mwsadmin/jui/css/jquery.ui.slider.css',
    'mwsadmin/jui/css/jquery.ui.tabs.css',
    'mwsadmin/jui/css/jquery.ui.datepicker.css',
    'mwsadmin/jui/css/jquery.ui.button.css',
    # 'mw/sadmin/jui/css/jquery.ui.progressbar.css',
    # 'mwsadmin/jui/css/jquery.ui.timepicker.css',
    'mwsadmin/jui/css/jquery.ui.theme.css',
)

# used theme css
theme_bundle_css = (
    'mwsadmin/css/reset.css',
    'mwsadmin/css/core/shared.css',
    'mwsadmin/css/core/core.css',
    'mwsadmin/css/core/panels.css',
    'mwsadmin/css/core/table.css',
    # 'mwsadmin/css/core/gallery.css',
    'mwsadmin/css/core/button.css',
    # 'mwsadmin/css/core/statistic.css',
    'mwsadmin/css/core/form.css',
    'mwsadmin/css/core/misc.css',
    'mwsadmin/css/core/plugins.css',
    'mwsadmin/css/core/responsive.css',
    'mwsadmin/css/fonts/ptsans/stylesheet.css',
    'mwsadmin/css/fluid.css',
    'mwsadmin/css/text.css',
    # 'mwsadmin/css/icons/16x16.css',
    # 'mwsadmin/css/icons/24x24.css',
    # 'mwsadmin/css/icons/32x32.css',
    'mwsadmin/plugins/chosen/chosen.css',
    'mwsadmin/plugins/jgrowl/jquery.jgrowl.css',
)

# used plugins + extra css
extra_theme_bundle_css = (
    'mwsadmin/plugins/inline_edit/css/inline_edit.css',
    'mwsadmin/plugins/input-and-choice/input-and-choice.css',
    'mwsadmin/plugins/jquerypasswordstrength/jquery.password_strength.css',
    'mwsadmin/plugins/screwdefaultbuttons/css/styles.css',

    'users/mwsadmin/css/dashboard.css',

    'mwsadmin/extra/css/extra.css',
    'mwsadmin/extra/css/icons/extra.16x16.css',
    'mwsadmin/extra/css/icons/extra.20x20.css',
    'mwsadmin/extra/css/icons/extra.24x24.css',
    'mwsadmin/extra/css/icons/extra.32x32.css',
    'mwsadmin/extra/css/views.css',

    'cases/mwsadmin/css/cases.css',
)

# jquery + jquery ui
jquery_bundle_js = (
    'mwsadmin/js/jquery-1.7.2.min.js',

    'mwsadmin/jui/js/jquery-ui.js',
    'mwsadmin/jui/js/jquery-ui-effects.min.js'
)

# used plugins + theme js
theme_bundle_js = (
    'mwsadmin/plugins/chosen/chosen.jquery.js',
    'mwsadmin/plugins/elastic/jquery.elastic.source.js',
    'mwsadmin/plugins/jgrowl/jquery.jgrowl.js',
    'mwsadmin/plugins/jqueryform/jquery.form.js',
    'mwsadmin/plugins/placeholder/jquery.placeholder.js',
    'mwsadmin/plugins/validate/jquery.validate.js',

    'mwsadmin/js/core/mws.js',
)

# non-standard plugins + custom js
extra_theme_bundle_js = (
    'mwsadmin/plugins/clickfocus/clickfocus.jquery.js',
    'mwsadmin/plugins/inline_edit/inline_edit.js',
    'mwsadmin/plugins/input-and-choice/input-and-choice.js',
    'mwsadmin/plugins/jquerypasswordstrength/jquery.password_strength.js',
    'mwsadmin/plugins/lilyformset/lily.formset.js',
    'mwsadmin/plugins/tabthis/tabthis.jquery.js',
    'mwsadmin/plugins/screwdefaultbuttons/js/jquery.screwdefaultbuttons.js',

    'mwsadmin/js/getsatisfaction.js',
    'mwsadmin/js/send_form.js',

    # js from apps
    'mwsadmin/extra/js/apps.js',

    'accounts/mwsadmin/js/account_dataprovider.js',
    'accounts/mwsadmin/js/account_exists.js',

    'accounts/mwsadmin/js/accounts.js',

    'contacts/mwsadmin/js/contacts.js',
    'mwsadmin/plugins/smartwizard/js/jquery.smartWizard-2.0.js',

    'cases/mwsadmin/js/cases.js',

    'deals/mwsadmin/js/deals.js',

    'notes/mwsadmin/js/notes.js',

    'provide/mwsadmin/js/dataprovider.js',

    'utils/mwsadmin/js/utils.js',

    'mwsadmin/plugins/historylist/historylist.js',
)

MEDIA_BUNDLES = (
    # typography css
    ('typography.css',
        'mwsadmin/css/reset.css',
        'mwsadmin/css/text.css',
    ),
    # iframe base
    ('theme.css',
    )   + jquery_bundle_css
        # + theme_bundle_css
        + extra_theme_bundle_css,
    # app css
    ('main.css',
    )   + jquery_bundle_css
        + theme_bundle_css
        + extra_theme_bundle_css,
    ('lily.accounts.css',
        'accounts/mwsadmin/css/account_dataprovider.css',
        'accounts/mwsadmin/css/accounts.css',
        'accounts/mwsadmin/css/responsive.css',
    ),
    ('lily.contacts.css',
        'contacts/mwsadmin/css/contacts.css',
        'contacts/mwsadmin/css/responsive.css',
        'mwsadmin/plugins/smartwizard/styles/smart_wizard.css',
    ),
    ('lily.deals.css',
        'deals/mwsadmin/css/deals.css',
    ),
    ('lily.users.css',
        'mwsadmin/css/core/login.css',
        'users/mwsadmin/css/activation.css',
        'users/mwsadmin/css/invitation.css',
        'users/mwsadmin/css/password_reset.css',
    ),
    ('error.css',
        'mwsadmin/css/core/error.css',
    ),
    ('main.js',
        # {'filter': 'mediagenerator.filters.media_url.MediaURL'}, makes +/- 430 KB difference
    )   + jquery_bundle_js
        + theme_bundle_js
        + extra_theme_bundle_js
        + ({'filter': 'mediagenerator.filters.i18n.I18N'},
           'mwsadmin/js/jquery.fileinput.js',),
    ('tables.js',
        'mwsadmin/js/diacritics.js',
        'mwsadmin/plugins/datatables/jquery.dataTables.js',
        'mwsadmin/plugins/datatables/jquery.dataTables.date.js',
    ),
    ('lily.dashboard.js',
        'users/mwsadmin/js/dashboard.js',
    ),
    ('lily.users.js',
        'users/mwsadmin/js/activation.js',
        'users/mwsadmin/js/invitation.js',
        'users/mwsadmin/js/login.js',
        'users/mwsadmin/js/password_reset.js',
        'users/mwsadmin/js/registration.js',
    ),
    ('lily.messaging.css',
        'messaging/mwsadmin/css/messaging.css',
    ),
    ('lily.messaging.js',
        'messaging/mwsadmin/js/messaging.js',
    ),
    ('hallojs.css',
        'mwsadmin/plugins/hallojs/hallo.css',
        # 'mwsadmin/plugins/hallojs/image.css',
        'mwsadmin/plugins/fontawesome/css/font-awesome.css',
        'mwsadmin/plugins/hallojs/hallo-extra.css',
    ),
    ('hallojs-ie7.css',
        'mwsadmin/plugins/fontawesome/css/font-awesome-ie7.css',
    ),
    ('hallojs.js',
        'mwsadmin/plugins/rangy/rangy-core.js',
        'mwsadmin/plugins/hallojs/hallo.js',
    ),
#    ('translations.js',
#         {'filter': 'mediagenerator.filters.i18n.I18N'},
#    ),
)
