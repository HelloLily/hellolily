angular.module('app.forms.directives').directive('formEmailAddresses', formEmailAddresses);

function formEmailAddresses() {
    return {
        restrict: 'E',
        require: '^form',
        scope: {
            emailAddresses: '=',
            addRelatedField: '&',
            removeRelatedField: '&',
        },
        templateUrl: 'forms/directives/email_addresses.html',
        controller: FormEmailAddressesController,
        controllerAs: 'vm',
        bindToController: true,
        link: function(scope, element, attrs, form) {
            // Set parent form on the scope
            scope.form = form;
        },
    };
}

FormEmailAddressesController.$inject = ['$rootScope'];
function FormEmailAddressesController($rootScope) {
    var vm = this;
    vm.sidebar = $rootScope.$$childHead.emailSettings.sidebar.form;

    vm.setPrimaryEmailAddress = setPrimaryEmailAddress;

    activate();

    /////

    function activate() {
        if (vm.sidebar == 'createContact') {
            vm.emailLabel = 'Email';
        } else {
            vm.emailLabel = 'Company email';
        }
    }

    function setPrimaryEmailAddress(emailAddress) {
        // Check if the status of an email address is 'Primary'
        if (emailAddress.status === 2) {
            angular.forEach(vm.emailAddresses, function(email) {
                // Set the status of the other email addresses to 'Other'
                if (emailAddress !== email) {
                    email.status = 1;
                }
            });
        }
    }
}
