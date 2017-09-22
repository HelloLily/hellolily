angular.module('app.preferences').config(tenantSettings);

tenantSettings.$inject = ['$stateProvider'];
function tenantSettings($stateProvider) {
    $stateProvider.state('base.preferences.admin.settings', {
        url: '/settings',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/admin/settings/settings_temp.html',
                controller: TenantSettingsController,
                controllerAs: 'vm',
            },
        },
    });
}

angular.module('app.preferences').controller('TenantSettingsController', TenantSettingsController);

TenantSettingsController.$inject = ['$http', '$injector', '$scope', '$state', '$window', 'HLForms'];
function TenantSettingsController($http, $injector, $scope, $state, $window, HLForms) {
    var vm = this;

    vm.saveField = saveField;
    vm.moveUp = moveUp;
    vm.moveDown = moveDown;

    activate();

    ////

    function activate() {
        let settings = [
            {
                model: 'Account',
                fields: {
                    'statuses': [],
                },
            },
            {
                model: 'Case',
                fields: {
                    'statuses': [],
                    'caseTypes': [],
                },
            },
            {
                model: 'Deal',
                fields: {
                    'contactedBy': [],
                    'foundThrough': [],
                    'nextSteps': [],
                    'statuses': [],
                    'whyCustomer': [],
                    'whyLost': [],
                },
            },
        ];

        settings.forEach(setting => {
            const resource = $injector.get(setting.model);

            for (let key in setting.fields) {
                const action = 'get' + key.charAt(0).toUpperCase() + key.slice(1);
                resource[action]().$promise.then(response => {
                    setting.fields[key] = response.results;
                });
            }
        });

        vm.settings = settings;
    }

    function moveUp(index, items) {
        if (index > 0) {
            let oldItem = items[index];
            items[index].position = items[index - 1].position;
            items[index - 1].position = oldItem.position;

            items[index] = items[index - 1];
            items[index - 1] = oldItem;
        }
    }

    function moveDown(index, items) {
        if (index < items.length) {
            let oldItem = items[index];
            items[index].position = items[index + 1].position;
            items[index + 1].position = oldItem.position;

            items[index] = items[index + 1];
            items[index + 1] = oldItem;
        }
    }

    function saveField(model, field) {
        HLForms.blockUI();

        // All urls have the same format and the fields are in camelCase.
        // Replace the uppercase letter with a lower case letter with a dash in front of it.
        const endpoint = field.replace(/[A-Z]/g, '-$1');
        const url = `/api/${model.toLowerCase()}s/${endpoint}/`;
        const modelSettings = vm.settings.find(setting => setting.model === model);

        const config = {
            headers: {
                // Needed for drf-extensions to accept a bulk operation.
                'X-BULK-OPERATION': true,
            },
        };

        $http.patch(url, modelSettings.fields[field], config).then(response => {
            $state.reload();
        }, error => {
            Metronic.unblockUI();
        });
    }
}
