angular.module('app.preferences').controller('PreferencesSetTemplateDefaultModal', PreferencesSetTemplateDefaultModal);

PreferencesSetTemplateDefaultModal.$inject = ['$uibModalInstance', 'HLForms', 'EmailTemplate', 'emailTemplate', 'emailAccountList'];
function PreferencesSetTemplateDefaultModal($uibModalInstance, HLForms, EmailTemplate, emailTemplate, emailAccountList) {
    var vm = this;
    vm.emailTemplate = emailTemplate;
    vm.emailAccountList = emailAccountList;
    vm.ok = ok;
    vm.cancel = cancel;

    activate();

    /////

    function activate() {
        vm.emailAccountList.forEach(function(emailAccount) {
            // For every email account in emailTemplate.default_for set selected to true.
            var selected = emailTemplate.default_for.filter(function(obj) {
                return obj.id === emailAccount.id;
            });
            emailAccount.selected = selected.length > 0;
        });
    }

    function ok(form) {
        var selectedAccounts = [];

        // Loop over emailAccountList to extract the selected accounts.
        vm.emailAccountList.forEach(function(emailAccount) {
            if (emailAccount.selected) {
                selectedAccounts.push(emailAccount.id);
            }
        });

        vm.emailTemplate.default_for = selectedAccounts;

        // Use the EmailTemplate resource for updating the default_for attribute.
        EmailTemplate.update({id: vm.emailTemplate.id}, vm.emailTemplate, function() {
            $uibModalInstance.close(vm.emailTemplate);
            toastr.success('I\'ve updated the email template for you!', 'Done');
        }, function(response) {
            HLForms.setErrors(form, response.data);
            toastr.error('Uh oh, there seems to be a problem', 'Oops!');
        });
    }

    // Let's not change anything.
    function cancel() {
        $uibModalInstance.dismiss('cancel');
    }
}
