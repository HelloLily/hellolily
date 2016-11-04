angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.emailtemplates.create', {
        url: '/create',
        views: {
            '@base.preferences': {
                templateUrl: '/messaging/email/templates/create/',
                controller: PreferencesEmailTemplatesCreateUpdate,
            },
        },
        ncyBreadcrumb: {
            label: 'Email template create',
        },
    });

    $stateProvider.state('base.preferences.emailtemplates.edit', {
        url: '/edit/{id:[0-9]{1,}}',
        views: {
            '@base.preferences': {
                templateUrl: function(elem, attr) {
                    return '/messaging/email/templates/update/' + elem.id + '/';
                },
                controller: PreferencesEmailTemplatesCreateUpdate,
            },
        },
        ncyBreadcrumb: {
            label: 'Email template edit',
        },
    });
}

angular.module('app.preferences').controller('PreferencesEmailTemplatesCreateUpdate', PreferencesEmailTemplatesCreateUpdate);

// TODO: LILY-XXX: Try to change the openVariable and closeVariable to curly braces, so it's consistent with other templating engines
PreferencesEmailTemplatesCreateUpdate.$inject = ['$scope'];
function PreferencesEmailTemplatesCreateUpdate($scope) {
    HLInbox.init();
    HLInbox.initWysihtml5();
    HLEmailTemplates.init({
        parseEmailTemplateUrl: '',
        openVariable: '[[',
        closeVariable: ']]',
    });

    // Listen to Angular broadcast function on scope destroy.
    $scope.$on('$destroy', function() {
        // Properly destroy the rich text editor to prevent memory leaks.
        HLInbox.destroyEditor();
    });
}

