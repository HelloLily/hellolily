angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.emailtemplates', {
        url: '/emailtemplates',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/controllers/emailtemplate_list.html',
                controller: PreferencesEmailTemplatesList,
                controllerAs: 'vm',
                bindToController: true,
            },
        },
        ncyBreadcrumb: {
            label: 'Email templates',
        },
    });
}

angular.module('app.preferences').controller('PreferencesEmailTemplatesList', PreferencesEmailTemplatesList);

PreferencesEmailTemplatesList.$inject = ['$uibModal', '$scope', 'EmailTemplate'];
function PreferencesEmailTemplatesList($uibModal, $scope, EmailTemplate) {
    var vm = this;

    vm.makeDefault = makeDefault;
    vm.deleteEmailTemplate = deleteEmailTemplate;

    activate();

    //////

    function activate() {
        EmailTemplate.query({}, function(data) {
            vm.emailTemplates = data.results;
        });
    }

    function makeDefault(emailTemplate) {
        // TODO: LILY-756: Make this controller more Angular
        var modalInstance = $uibModal.open({
            templateUrl: '/messaging/email/templates/set-default/' + emailTemplate.id + '/',
            controller: 'PreferencesSetTemplateDefaultModal',
            size: 'lg',
            resolve: {
                emailTemplate: function() {
                    return emailTemplate;
                },
            },
        });

        modalInstance.result.then(function() {
            $state.go($state.current, {}, {reload: false});
        }, function() {
        });
    }

    function deleteEmailTemplate(emailtemplate) {
        if (confirm('Are you sure?')) {
            EmailTemplate.delete({
                id: emailtemplate.id,
            }, function() {  // On success
                var index = $scope.emailTemplates.indexOf(emailtemplate);
                $scope.emailTemplates.splice(index, 1);
            }, function(error) {  // On error
                alert('something went wrong.');
            });
        }
    }
}
