angular.module('app.preferences').config(pandaDocConfig);

pandaDocConfig.$inject = ['$stateProvider'];
function pandaDocConfig($stateProvider) {
    $stateProvider.state('base.preferences.admin.integrations.pandadoc', {
        url: '/pandadoc',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/admin/integrations/pandadoc.html',
                controller: PreferencesPandaDocController,
                controllerAs: 'vm',
            },
        },
    });
}

angular.module('app.preferences').controller('PreferencesPandaDocController', PreferencesPandaDocController);

PreferencesPandaDocController.$inject = ['$http', '$window', 'HLForms'];
function PreferencesPandaDocController($http, $window, HLForms) {
    var vm = this;

    vm.client_id = '';
    vm.client_secret = '';

    vm.getAccessToken = getAccessToken;

    function getAccessToken(form) {
        HLForms.clearErrors(form);

        // Try to store the credentials so we can reuse them later.
        $http({
            method: 'POST',
            url: '/api/integrations/auth/pandadoc',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            data: 'client_id=' + vm.client_id + '&client_secret=' + vm.client_secret,
        }).success(function(response) {
            // Everything was ok, so go to the PandaDoc authentication page.
            $window.location.href = decodeURIComponent(response.url);
        }).error(function(response) {
            HLForms.setErrors(form, response);
        });
    }
}
