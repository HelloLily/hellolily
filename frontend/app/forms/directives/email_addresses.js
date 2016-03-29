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

FormEmailAddressesController.$inject = ['$rootScope', 'HLUtils'];
function FormEmailAddressesController($rootScope, HLUtils) {
    var vm = this;
    vm.sidebar = $rootScope.$$childHead.settings.email.sidebar.form;

    vm.setPrimaryEmailAddress = HLUtils.setPrimaryEmailAddress;

    activate();

    /////

    function activate() {
        if (vm.sidebar === 'contact') {
            vm.emailLabel = 'Email';
        } else {
            vm.emailLabel = 'Company email';
        }
    }
}
