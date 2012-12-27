# used jquery css
jquery_bundle_css = (
    'jui/css/jquery.ui.core.css',
    'jui/css/jquery.ui.resizable.css',
#    'jui/css/jquery.ui.accordion.css',
    'jui/css/jquery.ui.autocomplete.css',
    'jui/css/jquery.ui.dialog.css',
#    'jui/css/jquery.ui.slider.css',
    'jui/css/jquery.ui.tabs.css',
    'jui/css/jquery.ui.datepicker.css',
    'jui/css/jquery.ui.button.css',
#    'jui/css/jquery.ui.progressbar.css',
#    'jui/css/jquery.ui.timepicker.css',
    'jui/css/jquery.ui.theme.css',
)

# used theme css
theme_bundle_css = (
    'css/reset.css',
    'css/core/shared.css',
    'css/core/core.css',
    'css/core/panels.css',
    'css/core/table.css',
#    'css/core/gallery.css',
    'css/core/button.css',
#    'css/core/statistic.css',
    'css/core/form.css',
    'css/core/misc.css',
    'css/core/plugins.css',
    'css/core/responsive.css',
    'css/fonts/ptsans/stylesheet.css',
    'css/fluid.css',
    'css/text.css',
#    'css/icons/16x16.css',
#    'css/icons/24x24.css',
#    'css/icons/32x32.css',
    'plugins/chosen/chosen.css',
    'plugins/jgrowl/jquery.jgrowl.css',
)

# used plugins + extra css
extra_theme_bundle_css = (
    'plugins/inline_edit/css/inline_edit.css',
    'plugins/input-and-choice/input-and-choice.css',
    'plugins/jquerypasswordstrength/jquery.password_strength.css',
    'plugins/screwdefaultbuttons/css/styles.css',

    'users/css/dashboard.css',

    'extra/css/extra.css',
    'extra/css/icons/extra.16x16.css',
#    'extra/css/icons/extra.20x20.css',
    'extra/css/icons/extra.24x24.css',
    'extra/css/icons/extra.32x32.css',
    'extra/css/views.css',

    'cases/css/cases.css',
)

# jquery + jquery ui
jquery_bundle_js = (
    'js/jquery-1.7.2.min.js',

    'jui/js/jquery-ui.js',
    'jui/js/jquery-ui-effects.min.js'
)

# used plugins + theme js
theme_bundle_js = (
    'plugins/chosen/chosen.jquery.js',
    'plugins/elastic/jquery.elastic.source.js',
    'plugins/jgrowl/jquery.jgrowl.js',
    'plugins/jqueryform/jquery.form.js',
    'plugins/placeholder/jquery.placeholder.js',
    'plugins/validate/jquery.validate.js',

    'js/core/mws.js',
)

# non-standard plugins + custom js
extra_theme_bundle_js = (
    'plugins/clickfocus/clickfocus.jquery.js',
    'plugins/inline_edit/inline_edit.js',
    'plugins/input-and-choice/input-and-choice.js',
    'plugins/jquerypasswordstrength/jquery.password_strength.js',
    'plugins/lilyformset/lily.formset.js',
    'plugins/tabthis/tabthis.jquery.js',
    'plugins/screwdefaultbuttons/js/jquery.screwdefaultbuttons.js',

    'js/getsatisfaction.js',
    'js/send_form.js',

    # js from apps
    'extra/js/apps.js',

    'accounts/js/account_dataprovider.js',
    'accounts/js/account_exists.js',

    'accounts/js/accounts.js',

    'contacts/js/contacts.js',

    'cases/js/cases.js',

    'deals/js/deals.js',

    'notes/js/notes.js',

    'provide/js/dataprovider.js',

    'utils/js/utils.js',

)

MEDIA_BUNDLES = (
    # typography css
    ('typography.css',
        'css/reset.css',
        'css/text.css',
    ),
    # app css
    ('main.css',
    )   + jquery_bundle_css
        + theme_bundle_css
        + extra_theme_bundle_css,
    ('lily.accounts.css',
        'accounts/css/account_dataprovider.css',
        'accounts/css/accounts.css',
        'accounts/css/responsive.css',
    ),
    ('lily.contacts.css',
        'contacts/css/contacts.css',
        'contacts/css/responsive.css',
    ),
    ('lily.deals.css',
        'deals/css/deals.css',
    ),
    ('lily.users.css',
        'css/core/login.css',
        'users/css/activation.css',
        'users/css/invitation.css',
        'users/css/password_reset.css',
    ),
    ('error.css',
        'css/core/error.css',
    ),
    ('main.js',
#        {'filter': 'mediagenerator.filters.media_url.MediaURL'}, makes +/- 430 KB difference
    )   + jquery_bundle_js
        + theme_bundle_js
        + extra_theme_bundle_js
        + ({'filter': 'mediagenerator.filters.i18n.I18N'},
           'js/jquery.fileinput.js',),
    ('tables.js',
        'plugins/datatables/jquery.dataTables-min.js',
        'plugins/datatables/jquery.dataTables.date.js',
    ),
    ('lily.dashboard.js',
        'users/js/dashboard.js',
    ),
    ('lily.users.js',
        'users/js/activation.js',
        'users/js/invitation.js',
        'users/js/login.js',
        'users/js/password_reset.js',
        'users/js/registration.js',
    ),
    ('lily.messages.css',
        'messages/css/messages.css',
    ),
    ('lily.messages.js',
        'messages/js/messages.js',
    ),
#    ('translations.js',
#         {'filter': 'mediagenerator.filters.i18n.I18N'},
#    ),
)
