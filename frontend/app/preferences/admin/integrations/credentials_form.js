angular.module('app.preferences').directive('credentialsForm', credentialsForm);

function credentialsForm() {
    return {
        restrict: 'E',
        templateUrl: 'preferences/admin/integrations/credentials_form.html',
        controller: IntegrationCredentialsController,
        controllerAs: 'vm',
        bindToController: true,
        transclude: {
            integrationContext: '?integrationContext',
        },
    };
}

angular.module('app.preferences').controller('IntegrationCredentialsController', IntegrationCredentialsController);

IntegrationCredentialsController.$inject = ['$http', '$state', '$stateParams', '$window', 'HLForms'];
function IntegrationCredentialsController($http, $state, $stateParams, $window, HLForms) {
    var vm = this;

    vm.client_id = '';
    vm.client_secret = '';
    vm.integrationContext = {};
    vm.type = $stateParams.type;

    vm.getAccessToken = getAccessToken;
    vm.cancelIntegration = cancelIntegration;

    function getAccessToken(form) {
        HLForms.clearErrors(form);

        // Try to store the credentials so we can reuse them later.
        $http({
            method: 'POST',
            url: `/api/integrations/auth/${vm.type.toLowerCase()}/`,
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            data: 'client_id=' + vm.client_id + '&client_secret=' + vm.client_secret + '&integration_context=' + JSON.stringify(vm.integrationContext),
        }).success(response => {
            // Everything was ok, so go to the authentication page.
            $window.location.href = decodeURIComponent(response.url);
        }).error(response => {
            HLForms.setErrors(form, response);
        });
    }

    function cancelIntegration() {
        $state.go('base.preferences.admin.integrations');
    }
}

