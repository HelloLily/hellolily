angular.module('app.forms.directives').directive('formAddresses', formAddresses);

function formAddresses() {
    return {
        restrict: 'E',
        require: '^form',
        scope: {
            addresses: '=',
            addRelatedField: '&',
            removeRelatedField: '&'
        },
        templateUrl: 'forms/directives/addresses.html',
        controller: FormAddressesController,
        controllerAs: 'vm',
        bindToController: true,
        link: function (scope, element, attrs, form) {
            // Set parent form on the scope
            scope.form = form;
        }
    }
}

function FormAddressesController() {
    var vm = this;
    vm.addressTypes = [
        {key: 'visiting', value: 'Visiting address'},
        {key: 'billing', value: 'Billing address'},
        {key: 'shipping', value: 'Shipping address'},
        {key: 'home', value: 'Home address'},
        {key: 'other', value: 'Other'}
    ];

}
