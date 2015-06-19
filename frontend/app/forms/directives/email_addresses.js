angular.module('app.forms.directives').directive('formEmailAddresses', formEmailAddresses);

function formEmailAddresses() {
    return {
        restrict: 'E',
        scope: {
            emailAddresses: '=',
            addRelatedField: '&',
            removeRelatedField: '&'
        },
        templateUrl: 'forms/directives/email_addresses.html',
        controller: FormEmailAddressesController,
        controllerAs: 'vm',
        bindToController: true
    }
}

function FormEmailAddressesController() {
    var vm = this;
    vm.setPrimaryEmailAddress = setPrimaryEmailAddress;

    /////

    function setPrimaryEmailAddress (emailAddress) {
        // Check if the status of an email address is 'Primary'
        if (emailAddress.status == 0) {
            angular.forEach(vm.emailAddresses, function(email) {
                // Set the status of the other email addresses to 'Other'
                if (emailAddress != email) {
                    email.status = 1;
                }
            });
        }
    }
}
