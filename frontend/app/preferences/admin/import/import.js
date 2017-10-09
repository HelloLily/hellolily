require('ng-file-upload');

angular.module('app.preferences').config(importConfig);

importConfig.$inject = ['$stateProvider'];
function importConfig($stateProvider) {
    $stateProvider.state('base.preferences.admin.import', {
        // parent: 'base.preferences.user',
        url: '/import',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/admin/import/import.html',
                controller: PreferencesImportController,
                controllerAs: 'vm',
            },
        },

    });
}

angular.module('app.preferences').controller('PreferencesImportController', PreferencesImportController);

PreferencesImportController.$inject = ['HLForms', 'HLUtils', 'Upload'];
function PreferencesImportController(HLForms, HLUtils, Upload) {
    var vm = this;
    vm.csv = null;
    vm.import_result_error = null;
    vm.import_result_duplicate = null;
    vm.import_result_created = null;

    vm.importAccounts = importAccounts;

    //////

    function importAccounts(form) {
        var formName = '[name="importForm"]';

        var data = {};

        if (vm.csv instanceof File) {
            data.csv = vm.csv;
        }

        HLUtils.blockUI(formName, true);
        HLForms.clearErrors(form);

        // Reset message for a previous upload.
        vm.import_result_error = null;
        vm.import_result_duplicate = null;
        vm.import_result_created = null;

        Upload.upload({
            url: 'api/accounts/import/',
            method: 'POST',
            data: data,
        }).then(function(response) {
            HLUtils.unblockUI(formName);
            toastr.success('I\'ve imported your accounts!', 'Done');

            if (response.data.error) {
                vm.import_result_error = response.data.error;
            }
            if (response.data.duplicate) {
                vm.import_result_duplicate = response.data.duplicate;
            }
            if (response.data.created) {
                vm.import_result_created = response.data.created;
            }
        }, function(response) {
            HLUtils.unblockUI(formName);
            if (response) {
                HLForms.setErrors(form, response.data);
            }

            toastr.error('Uh oh, there seems to be a problem', 'Oops!');
        });
    }
}
