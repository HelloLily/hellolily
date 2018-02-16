angular.module('app.directives').directive('toggleActivationContact', toggleActivationContact);
function toggleActivationContact() {
    return {
        restrict: 'E',
        scope: {
            model: '@',
            object: '=',
            displayField: '@?',
            callback: '&?',
            buttonClass: '@?',
            iconClass: '@?',
            messageObject: '=?',
            helpText: '@?',
        },
        templateUrl: 'contacts/directives/toggle_activation_contact.html',
        controller: ToggleActivationContactController,
        controllerAs: 'vm',
        transclude: true,
        bindToController: true,
    };
}

ToggleActivationContactController.$inject = ['$compile', '$scope', '$state', '$templateCache', 'HLResource'];
function ToggleActivationContactController($compile, $scope, $state, $templateCache, HLResource) {
    const vm = this;

    vm.openToggleActivationModal = openToggleActivationModal;

    //////

    function openToggleActivationModal() {
        swal({
            title: '',
            html: $compile($templateCache.get('contacts/directives/contact_working_at_account.html'))($scope),
            showCloseButton: true,
            showCancelButton: true,
            confirmButtonText: 'Save',
        }).then(isConfirm => {
            if (isConfirm) {
                const args = {
                    id: vm.object.id,
                    functions: vm.object.functions,
                };

                HLResource.patch('Contact', args).$promise.then(() => {
                    $state.reload();
                });
            }
        }).done();
    }
}
