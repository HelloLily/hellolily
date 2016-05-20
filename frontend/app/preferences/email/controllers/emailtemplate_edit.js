angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.emailtemplates.edit', {
        url: '/edit/{id:[0-9]{1,}}',
        views: {
            '@base.preferences': {
                templateUrl: function(elem, attr) {
                    return '/messaging/email/templates/update/' + elem.id + '/';
                },
                controller: PreferencesEmailTemplatesEdit,
            },
        },
        ncyBreadcrumb: {
            label: 'Email template edit',
        },
    });
}

angular.module('app.preferences').controller('PreferencesEmailTemplatesEdit', PreferencesEmailTemplatesEdit);

// TODO: LILY-XXX: Try to change the openVariable and closeVariable to curly braces, so it's consistent with other templating engines
function PreferencesEmailTemplatesEdit() {
    HLInbox.init();
    HLInbox.initWysihtml5();
    HLEmailTemplates.init({
        parseEmailTemplateUrl: '',
        openVariable: '[[',
        closeVariable: ']]',
    });
}

