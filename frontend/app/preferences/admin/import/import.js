require('ng-file-upload');

angular.module('app.preferences').config(importConfig);

importConfig.$inject = ['$stateProvider'];
function importConfig($stateProvider) {
    $stateProvider.state('base.preferences.admin.import', {
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
    const vm = this;

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
        const formName = '[name="importAccountsForm"]';

        const data = {};

        if (vm.csv instanceof File) {
            data.csv = vm.csv;
        }

        HLUtils.blockUI(formName, true);
        HLForms.clearErrors(form);

        // Reset message for a previous upload.
        vm.import_accounts_result_error = null;
        vm.import_accounts_result_created_updated = null;

        Upload.upload({
            url: 'api/accounts/import/',
            method: 'POST',
            data: data,
        }).then(response => {
            HLUtils.unblockUI(formName);
            toastr.success(messages.notifications.importSuccess, messages.notifications.successTitle);

            if (response.data.error) {
                vm.import_accounts_result_error = response.data.error;
            }
            if (response.data.created_updated) {
                vm.import_accounts_result_created_updated = response.data.created_updated;
            }
        }, response => {
            HLUtils.unblockUI(formName);

            if (response) {
                HLForms.setErrors(form, response.data);
            }

            toastr.error(messages.notifications.error, messages.notifications.errorTitle);
        });
    }

    function importContacts(form) {
        const formName = '[name="importContactsForm"]';

        const data = {};

        if (vm.csv instanceof File) {
            data.csv = vm.csv;
        }

        HLUtils.blockUI(formName, true);
        HLForms.clearErrors(form);

        // Reset message for a previous upload.
        vm.import_contacts_result_error = null;
        vm.import_contacts_result_duplicate = null;
        vm.import_contacts_result_created = null;

        Upload.upload({
            data,
            url: 'api/contacts/import/',
            method: 'POST',
        }).then(response => {
            HLUtils.unblockUI(formName);
            toastr.success(messages.notifications.contactImportSuccess, messages.notifications.successTitle);

            if (response.data.error) {
                vm.import_contacts_result_error = response.data.error;
            }
            if (response.data.duplicate) {
                vm.import_contacts_result_duplicate = response.data.duplicate;
            }
            if (response.data.created) {
                vm.import_contacts_result_created = response.data.created;
            }
        }, response => {
            HLUtils.unblockUI(formName);
            if (response) {
                HLForms.setErrors(form, response.data);
            }

            toastr.error(messages.notifications.error, messages.notifications.errorTitle);
        });
    }
}
