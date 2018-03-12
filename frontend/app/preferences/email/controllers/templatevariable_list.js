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

PreferencesEmailTemplatesList.$inject = ['$scope', 'Settings', 'TemplateVariable', 'user'];
function PreferencesEmailTemplatesList($scope, Settings, TemplateVariable, user) {
    const vm = this;

    Settings.page.setAllTitles('list', 'email template variables');

    vm.templateVariables = [];
    vm.publicTemplateVariables = [];

    vm.removeFromList = removeFromList;
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

    function removeFromList(templateVariable) {
        var index = vm.templateVariables.indexOf(templateVariable);
        vm.templateVariables.splice(index, 1);

        $scope.$apply();
    }

    function previewTemplateVariable(templateVariable) {
        swal('Preview', templateVariable.text).done();
    }
}
