angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.templatevariables', {
        url: '/templatevariables',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/controllers/templatevariable_list.html',
                controller: PreferencesEmailTemplatesList
            }
        },
        ncyBreadcrumb: {
            label: 'Template variables'
        }
    });
}

angular.module('app.preferences').controller('PreferencesTemplatesList', PreferencesEmailTemplatesList);

PreferencesEmailTemplatesList.$inject = ['$modal', '$scope', 'TemplateVariable'];
function PreferencesEmailTemplatesList ($modal, $scope, TemplateVariable) {
    //$scope.conf.pageTitleBig = 'EmailTemplate settings';
    //$scope.conf.pageTitleSmall = 'the devil is in the details';

    TemplateVariable.query({}, function(data) {
        // Split custom variables into separate arrays so it's easier to process in the template
        $scope.templateVariables = [];
        $scope.publicTemplateVariables = [];

        angular.forEach(data.custom, function (variable) {
            //
            if (variable.is_public && variable.owner != currentUser.id) {
                $scope.publicTemplateVariables.push(variable);
            } else {
                $scope.templateVariables.push(variable);
            }
        });

        $scope.currentUser = currentUser;
    });

    $scope.deleteTemplateVariable = function (templateVariable) {
        if (confirm('Are you sure?')) {
            TemplateVariable.delete({
                id: templateVariable.id
            }, function () {  // On success
                var index = $scope.templateVariables.indexOf(templateVariable);
                $scope.templateVariables.splice(index, 1);
            }, function (error) {  // On error
                alert('Something went wrong.')
            })
        }
    };

    $scope.previewTemplateVariable = function (templateVariable) {
        bootbox.alert(templateVariable.text);
    };
}
