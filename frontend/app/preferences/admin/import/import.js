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

PreferencesImportController.$inject = ['HLForms', 'HLUtils', 'Settings', 'Upload'];
function PreferencesImportController(HLForms, HLUtils, Settings, Upload) {
    const vm = this;

    Settings.page.setAllTitles('list', 'import');

    vm.csv = null;

    vm.import_accounts_result_error = null;
    vm.import_accounts_result_created_updated = null;

    vm.import_contacts_result_error = null;
    vm.import_contacts_result_duplicate = null;
    vm.import_contacts_result_created = null;

    vm.importAccounts = importAccounts;
    vm.importContacts = importContacts;

    //////

    function importAccounts(form) {
        var formName = '[name="importAccountsForm"]';

        var data = {};

        if (vm.csv instanceof File) {
            data.csv = vm.csv;
        }
        data.import_type = 'accounts';

        HLUtils.blockUI(formName, true);
        HLForms.clearErrors(form);

        // Reset message for a previous upload.
        vm.import_accounts_result_error = null;
        vm.import_accounts_result_created_updated = null;

        Upload.upload({
            url: 'api/import/',
            method: 'POST',
            data: data,
        }).then(function(response) {
            HLUtils.unblockUI(formName);
            toastr.success('I\'ve imported your accounts!', 'Done');

            if (response.data.error) {
                vm.import_accounts_result_error = response.data.error;
            }
            if (response.data.created_updated) {
                vm.import_accounts_result_created_updated = response.data.created_updated;
            }
        }, function(response) {
            HLUtils.unblockUI(formName);
            if (response) {
                HLForms.setErrors(form, response.data);
            }

            toastr.error('Uh oh, there seems to be a problem', 'Oops!');
        });
    }

    function importContacts(form) {
        var formName = '[name="importContactsForm"]';

        var data = {};

        if (vm.csv instanceof File) {
            data.csv = vm.csv;
        }
        data.import_type = 'contacts';

        HLUtils.blockUI(formName, true);
        HLForms.clearErrors(form);

        // Reset message for a previous upload.
        vm.import_contacts_result_error = null;
        vm.import_contacts_result_duplicate = null;
        vm.import_contacts_result_created = null;

        Upload.upload({
            url: 'api/import/',
            method: 'POST',
            data: data,
        }).then(function(response) {
            HLUtils.unblockUI(formName);
            toastr.success('I\'ve imported your contacts!', 'Done');

            if (response.data.error) {
                vm.import_contacts_result_error = response.data.error;
            }
            if (response.data.duplicate) {
                vm.import_contacts_result_duplicate = response.data.duplicate;
            }
            if (response.data.created) {
                vm.import_contacts_result_created = response.data.created;
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
