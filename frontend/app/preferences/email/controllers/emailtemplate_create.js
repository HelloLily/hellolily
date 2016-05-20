angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.emailtemplates.create', {
        url: '/create',
        views: {
            '@base.preferences': {
                templateUrl: '/messaging/email/templates/create/',
                controller: PreferencesEmailTemplatesCreate,
            },
        },
        ncyBreadcrumb: {
            label: 'Email template edit',
        },
    });
}

angular.module('app.preferences').controller('PreferencesEmailTemplatesCreate', PreferencesEmailTemplatesCreate);

// TODO: LILY-XXX: Try to change the openVariable and closeVariable to curly braces, so it's consistent with other templating engines
function PreferencesEmailTemplatesCreate() {
    HLInbox.init();
    HLInbox.initWysihtml5();
    HLEmailTemplates.init({
        parseEmailTemplateUrl: '',
        openVariable: '[[',
        closeVariable: ']]',
    });
}
