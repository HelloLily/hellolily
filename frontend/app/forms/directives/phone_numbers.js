angular.module('app.forms.directives').directive('formPhoneNumbers', formPhoneNumbers);

function formPhoneNumbers() {
    return {
        restrict: 'E',
        require: '^form',
        scope: {
            phoneNumbers: '=',
            addRelatedField: '&',
            removeRelatedField: '&',
            showIcon: '=',
            address: '=',
            blurCallback: '&?',
        },
        templateUrl: 'forms/directives/phone_numbers.html',
        controller: FormPhoneNumbersController,
        controllerAs: 'vm',
        bindToController: true,
        transclude: true,
        link: function(scope, element, attrs, form) {
            // Set parent form on the scope
            scope.form = form;
        },
    };
}

FormPhoneNumbersController.$inject = ['HLUtils'];
function FormPhoneNumbersController(HLUtils) {
    const vm = this;

    if (!vm.phoneNumbers.length) {
        vm.addRelatedField({field: 'phoneNumber'});
    }

    vm.telephoneTypes = [
        {key: 'work', value: 'Work'},
        {key: 'mobile', value: 'Mobile'},
        {key: 'home', value: 'Home'},
        {key: 'fax', value: 'Fax'},
        {key: 'other', value: 'Other'},
    ];

    vm.onBlur = onBlur;

    function onBlur(phoneNumber) {
        HLUtils.formatPhoneNumber(phoneNumber, vm.address);

        vm.blurCallback()(phoneNumber.number);
    }
}
