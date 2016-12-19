angular.module('app.preferences').config(adminConfig);

adminConfig.$inject = ['$stateProvider'];
function adminConfig($stateProvider) {
    $stateProvider.state('base.preferences.admin', {
        url: '/admin',
    });
}

angular.module('app.preferences').controller('PreferencesAdminController', PreferencesAdminController);

PreferencesAdminController.$inject = [];
function PreferencesAdminController() {
}
