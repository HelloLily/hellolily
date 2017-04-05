angular.module('app.forms.directives').directive('formAddresses', formAddresses);

function formAddresses() {
    return {
        restrict: 'E',
        require: '^form',
        scope: {
            addresses: '=',
            addRelatedField: '&',
            removeRelatedField: '&',
            showIcon: '=',
        },
        templateUrl: 'forms/directives/addresses.html',
        controller: FormAddressesController,
        controllerAs: 'vm',
        bindToController: true,
        transclude: true,
        link: function(scope, element, attrs, form) {
            // Set parent form on the scope
            scope.form = form;
        },
    };
}

FormAddressesController.$inject = [];
function FormAddressesController() {
    var vm = this;

    if (!vm.addresses.length) {
        vm.addRelatedField({field: 'address'});
    }

    vm.addressTypes = [
        {key: 'visiting', value: 'Visiting address'},
        {key: 'billing', value: 'Billing address'},
        {key: 'shipping', value: 'Shipping address'},
        {key: 'home', value: 'Home address'},
        {key: 'other', value: 'Other'},
    ];
}
