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
    var vm = this;

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

    vm.formatPhoneNumber = HLUtils.formatPhoneNumber;
}
