angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.templatevariables', {
        url: '/templatevariables',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/email/controllers/templatevariable_list.html',
                controller: PreferencesEmailTemplatesList,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Template variables',
        },
        resolve: {
            user: ['User', function(User) {
                return User.me().$promise;
            }],
        },
    });
}

angular.module('app.preferences').controller('PreferencesTemplatesList', PreferencesEmailTemplatesList);

PreferencesEmailTemplatesList.$inject = ['TemplateVariable', 'user'];
function PreferencesEmailTemplatesList(TemplateVariable, user) {
    var vm = this;

    vm.templateVariables = [];
    vm.publicTemplateVariables = [];

    vm.deleteTemplateVariable = deleteTemplateVariable;
    vm.previewTemplateVariable = previewTemplateVariable;
    vm.currentUser = user;

    activate();

    ////

    function activate() {
        _getTemplateVariables();
    }

    function _getTemplateVariables() {
        TemplateVariable.query({}, function(data) {
            // Split custom variables into separate arrays so it's easier to process in the template

            angular.forEach(data.custom, function(variable) {
                if (variable.is_public && variable.owner !== vm.currentUser.id) {
                    vm.publicTemplateVariables.push(variable);
                } else {
                    vm.templateVariables.push(variable);
                }
            });
        });
    }

    function deleteTemplateVariable(templateVariable) {
        if (confirm('Are you sure?')) {
            TemplateVariable.delete({
                id: templateVariable.id,
            }, function() {  // On success
                var index = vm.templateVariables.indexOf(templateVariable);
                vm.templateVariables.splice(index, 1);
            }, function(error) {  // On error
                alert('Something went wrong.');
            });
        }
    }

    function previewTemplateVariable(templateVariable) {
        bootbox.alert(templateVariable.text);
    }
}
