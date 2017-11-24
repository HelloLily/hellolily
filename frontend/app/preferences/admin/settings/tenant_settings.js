angular.module('app.preferences').config(tenantSettings);

tenantSettings.$inject = ['$stateProvider'];
function tenantSettings($stateProvider) {
    $stateProvider.state('base.preferences.admin.settings', {
        url: '/settings',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/admin/settings/tenant_settings.html',
                controller: TenantSettingsController,
                controllerAs: 'vm',
            },
        },
        resolve: {
            tenant: ['Tenant', Tenant => Tenant.query({}).$promise],
        },
    });
}

angular.module('app.preferences').controller('TenantSettingsController', TenantSettingsController);

TenantSettingsController.$inject = ['$state', '$window', 'HLForms', 'Tenant', 'tenant'];
function TenantSettingsController($state, $window, HLForms, Tenant, tenant) {
    const vm = this;

    vm.tenant = tenant;

    vm.saveSettings = saveSettings;

    function saveSettings() {
        HLForms.blockUI();

        const args = {
            id: vm.tenant.id,
            timelogging_enabled: vm.tenant.timelogging_enabled,
            billing_default: vm.tenant.billing_default,
        };

        Tenant.patch(args).$promise.then(() => {
            toastr.success(sprintf(messages.notifications.modelSaved, {model: 'settings'}), messages.notifications.successTitle);
        }, error => {
            toastr.error(messages.notifications.error, messages.notifications.errorTitle);
        });

        HLForms.unblockUI();
    }
}

