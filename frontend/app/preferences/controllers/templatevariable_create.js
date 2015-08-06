angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.templatevariables.create', {
        url: '/create',
        views: {
            '@base.preferences': {
                templateUrl: '/messaging/email/templatevariables/create/',
                controller: PreferencesTemplateVariablesCreate
            }
        },
        ncyBreadcrumb: {
            label: 'Template variable create'
        }
    });
}

angular.module('app.preferences').controller('PreferencesTemplateVariablesCreate', PreferencesTemplateVariablesCreate);

function PreferencesTemplateVariablesCreate () {
    HLInbox.init({textEditorId: 'id_text'});
    HLInbox.initWysihtml5();
    HLEmailTemplates.init({
        parseEmailTemplateUrl: '',
        openVariable: '[[',
        closeVariable: ']]',
        textEditorId: '#id_text'
    });
}
