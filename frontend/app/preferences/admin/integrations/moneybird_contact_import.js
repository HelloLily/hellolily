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
            tenant: ['Tenant', function(Tenant) {
                return Tenant.query({});
            }],
        },
    });
}

angular.module('app.preferences').controller('MoneybirdContactImportController', MoneybirdContactImportController);

MoneybirdContactImportController.$inject = ['$scope', 'Moneybird', 'tenant'];
function MoneybirdContactImportController($scope, Moneybird, tenant) {
    var vm = this;

    vm.tenant = tenant;
    vm.autoSync = true;

    vm.setupSync = setupSync;

    function setupSync() {
        Moneybird.setupSync({'auto_sync': vm.autoSync}).$promise.then(function(response) {
            if (response.import_started) {
                toastr.success('The import will continue in the background. Feel free to continue using Lily', 'Import started');
            }
        });
    }
}
