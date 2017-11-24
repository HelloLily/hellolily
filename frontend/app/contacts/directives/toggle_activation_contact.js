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

ToggleActivationContactController.$inject = ['$compile', '$scope', '$state', '$templateCache', 'HLResource', 'Contact'];
function ToggleActivationContactController($compile, $scope, $state, $templateCache, HLResource, Contact) {
    const vm = this;

    vm.openToggleActivationModal = openToggleActivationModal;
    vm.toggleActivationForContact = toggleActivationForContact;

    //////

    function openToggleActivationModal() {
        swal({
            title: '',
            html: $compile($templateCache.get('contacts/directives/contact_working_at_account.html'))($scope),
            showCloseButton: true,
            confirmButtonText: 'Close',
        }).done();
    }

    function toggleActivationForContact(account) {
        const args = {
            contact: vm.object.id,
            account: account.id,
            is_active: vm.object.active_at_account[account.id],
        };

        Contact.toggleActiveAtAccount(args).$promise.then(() => {
            toastr.success(sprintf(messages.notifications.modelUpdated, {model: 'contact'}), messages.notifications.successTitle);
        }, response => {
            toastr.error(messages.notifications.error, messages.notifications.errorTitle);
        });
    }
}
