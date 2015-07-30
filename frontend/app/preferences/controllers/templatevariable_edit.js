angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.templatevariables.edit', {
        url: '/edit/{id:[0-9]{1,}}',
        views: {
            '@base.preferences': {
                templateUrl: function(elem, attr) {
                    return '/messaging/email/templatevariables/update/' + elem.id +'/';
                },
                controller: PreferencesTemplateVariablesEdit
            }
        },
        ncyBreadcrumb: {
            label: 'Template variable edit'
        }
    });
}

angular.module('app.preferences').controller('PreferencesTemplateVariablesEdit', PreferencesTemplateVariablesEdit);

function PreferencesTemplateVariablesEdit () {
    HLInbox.init({textEditorId: 'id_text'});
    HLInbox.initWysihtml5();
    HLEmailTemplates.init({
        parseEmailTemplateUrl: '',
        openVariable: '[[',
        closeVariable: ']]'
    });
}
