angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.emailaccounts.edit', {
        url: '/edit/{id:[0-9]{1,}}',
        views: {
            '@base.preferences': {
                templateUrl: function(elem, attr) {
                    return 'messaging/email/accounts/update/' + elem.id;
                },
                controller: 'PreferencesEmailAccountEdit',
            },
        },
        ncyBreadcrumb: {
            label: 'Edit EmailAccount',
        },
    });
}

angular.module('app.preferences').controller('PreferencesEmailAccountEdit', PreferencesEmailAccountEdit);

function PreferencesEmailAccountEdit() {}
