angular.module('app.preferences').config(contactSync);

contactSync.$inject = ['$stateProvider'];
function contactSync($stateProvider) {
    $stateProvider.state('base.preferences.admin.integrations.moneybird.import', {
        url: '/import',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/admin/integrations/moneybird_contact_import.html',
                controller: MoneybirdContactImportController,
                controllerAs: 'vm',
            },
        },
        resolve: {
            tenant: ['Tenant', Tenant => Tenant.query({})],
        },
    });
}

angular.module('app.preferences').controller('MoneybirdContactImportController', MoneybirdContactImportController);

MoneybirdContactImportController.$inject = ['$scope', 'Moneybird', 'tenant'];
function MoneybirdContactImportController($scope, Moneybird, tenant) {
    const vm = this;

    vm.tenant = tenant;
    vm.autoSync = true;

    vm.setupSync = setupSync;

    function setupSync() {
        Moneybird.setupSync({'auto_sync': vm.autoSync}).$promise.then(response => {
            if (response.import_started) {
                toastr.success(messages.notifications.moneybirdImportStart, messages.notifications.moneybirdImportStartTitle);
            }
        });
    }
}
