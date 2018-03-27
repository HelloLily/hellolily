angular.module('app.forms.directives').directive('formEmailAddresses', formEmailAddresses);

function formEmailAddresses() {
    return {
        restrict: 'E',
        require: '^form',
        scope: {
            label: '@?',
            emailAddresses: '=',
            addRelatedField: '&',
            removeRelatedField: '&',
            showIcon: '=',
            blurCallback: '&?',
        },
        templateUrl: 'forms/directives/email_addresses.html',
        controller: FormEmailAddressesController,
        controllerAs: 'vm',
        bindToController: true,
        transclude: true,
        link: function(scope, element, attrs, form) {
            // Set parent form on the scope
            scope.form = form;
        },
    };
}

FormEmailAddressesController.$inject = ['HLUtils'];
function FormEmailAddressesController(HLUtils) {
    const vm = this;

    vm.onBlur = onBlur;

    if (vm.emailAddresses && !vm.emailAddresses.length) {
        vm.addRelatedField({field: 'emailAddress'});
    }

    vm.setPrimaryEmailAddress = HLUtils.setPrimaryEmailAddress;

    if (!vm.label) {
        vm.label = 'Company email';
    }

    function onBlur(emailAddress) {
        vm.blurCallback()(emailAddress);
    }
}
