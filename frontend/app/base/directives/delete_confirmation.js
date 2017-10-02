/**
 * Directive to show a confirmation box before deleting.
 */
angular.module('app.directives').directive('deleteConfirmation', deleteConfirmation);
function deleteConfirmation() {
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
        templateUrl: 'base/directives/delete_confirmation.html',
        controller: DeleteConfirmationController,
        controllerAs: 'vm',
        transclude: true,
        bindToController: true,
    };
}

DeleteConfirmationController.$inject = ['$state', 'HLResource', 'Settings'];
function DeleteConfirmationController($state, HLResource, Settings) {
    let vm = this;

    vm.openConfirmationModal = openConfirmationModal;

    activate();

    ////

    function activate() {
        if (!vm.buttonClass) {
            vm.buttonClass = '';
        }

        if (!vm.iconClass) {
            vm.iconClass = 'lilicon hl-trashcan-icon';
        }

        if (!vm.helpText) {
            vm.helpText = 'Delete';
        }

        if (vm.messageObject) {
            vm.messages = {
                confirmTitle: vm.messageObject.confirmTitle || messages.alerts.delete.confirmTitle,
                confirmText: vm.messageObject.confirmText || messages.alerts.delete.confirmText,
                confirmButtonText: vm.messageObject.confirmButtonText || messages.alerts.delete.confirmButtonText,
                errorTitle: vm.messageObject.errorTitle || messages.alerts.general.errorTitle,
                errorText: vm.messageObject.errorText || messages.alerts.general.errorText,
                successTitle: vm.messageObject.successTitle || messages.alerts.delete.successTitle,
                successText: vm.messageObject.successText || messages.alerts.delete.successText,
            };
        } else {
            vm.messages = messages.alerts.delete;
        }
    }

    function openConfirmationModal() {
        let name = '';

        if (vm.displayField) {
            name = vm.object[vm.displayField];
        } else if (vm.object.hasOwnProperty('name')) {
            name = vm.object.name;
        } else if (vm.object.hasOwnProperty('full_name')) {
            name = vm.object.full_name;
        }

        swal({
            title: vm.messages.confirmTitle,
            html: sprintf(vm.messages.confirmText, {name: name ? name : 'this ' + vm.model.toLowerCase()}),
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#f3565d',
            confirmButtonText: vm.messages.confirmButtonText,
            preConfirm: () => {
                swal.enableLoading();
                return new Promise(resolve => {
                    HLResource.delete(vm.model, vm.object).then(() => {
                        // Delete was successful, so continue.
                        resolve();
                    }, error => {
                        // Otherwise show error alert.
                        swal({
                            title: vm.messages.errorTitle,
                            html: vm.messages.errorText,
                            type: 'error',
                        });
                    });
                });
            },
        }).then(isConfirm => {
            if (isConfirm) {
                // In certain cases we want to call a function of another controller.
                if (vm.callback) {
                    // Call the given function.
                    vm.callback();
                } else {
                    if (Settings.page.previousState && !Settings.page.previousState.state.name.endsWith('edit')) {
                        // Go to the previous page if it isn't the edit page of the just deleted item.
                        $state.go(Settings.page.previousState.state, Settings.page.previousState.params);
                    } else {
                        // Otherwise just go to the list view, which is the parent state.
                        $state.go($state.current.parent);
                    }
                }
            }
        }).done();
    }
}
