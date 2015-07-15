angular.module('app.forms.directives').directive('formPhoneNumbers', formPhoneNumbers);

function formPhoneNumbers() {
    return {
        restrict: 'E',
        require: '^form',
        scope: {
            phoneNumbers: '=',
            addRelatedField: '&',
            removeRelatedField: '&'
        },
        templateUrl: 'forms/directives/phone_numbers.html',
        controller: FormPhoneNumbersController,
        controllerAs: 'vm',
        bindToController: true,
        link: function (scope, element, attrs, form) {
            // Set parent form on the scope
            scope.form = form;
        }
    }
}

function FormPhoneNumbersController() {
    var vm = this;
    vm.telephoneTypes = [
        {key: 'work', value: 'Work'},
        {key: 'mobile', value: 'Mobile'},
        {key: 'home', value: 'Home'},
        {key: 'fax', value: 'Fax'},
        {key: 'other', value: 'Other'}
    ];
}
