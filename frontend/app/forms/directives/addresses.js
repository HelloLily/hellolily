angular.module('app.forms.directives').directive('formAddresses', formAddresses);

function formAddresses() {
    return {
        restrict: 'E',
        scope: {
            addresses: '=',
            addRelatedField: '&',
            removeRelatedField: '&'
        },
        templateUrl: 'forms/directives/addresses.html',
        controller: FormAddressesController,
        controllerAs: 'vm',
        bindToController: true
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
