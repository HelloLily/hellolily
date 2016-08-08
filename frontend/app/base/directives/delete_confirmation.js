require('sweetalert2');

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

DeleteConfirmationController.$inject = ['$state', 'HLMessages', 'HLResource', 'Settings'];
function DeleteConfirmationController($state, HLMessages, HLResource, Settings) {
    var vm = this;

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
                'confirmTitle': vm.messageObject.confirmTitle || HLMessages.alerts.delete.confirmTitle,
                'confirmText': vm.messageObject.confirmText || HLMessages.alerts.delete.confirmText,
                'confirmButtonText': vm.messageObject.confirmButtonText || HLMessages.alerts.delete.confirmButtonText,
                'errorTitle': vm.messageObject.errorTitle || HLMessages.alerts.delete.errorTitle,
                'errorText': vm.messageObject.errorText || HLMessages.alerts.delete.errorText,
                'successTitle': vm.messageObject.successTitle || HLMessages.alerts.delete.successTitle,
                'successText': vm.messageObject.successText || HLMessages.alerts.delete.successText,
            };
        } else {
            vm.messages = HLMessages.alerts.delete;
        }
    }

    function openConfirmationModal() {
        var name = '';

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
            preConfirm: function() {
                swal.enableLoading();
                return new Promise(function(resolve) {
                    HLResource.delete(vm.model, vm.object).then(function() {
                        // Delete was successful, so continue.
                        resolve();
                    }, function(error) {
                        // Otherwise show error alert.
                        swal({
                            title: vm.messages.errorTitle,
                            html: vm.messages.errorText,
                            type: 'error',
                        });
                    });
                });
            },
        }).then(function(isConfirm) {
            if (isConfirm) {
                swal({
                    title: vm.messages.successTitle,
                    html: sprintf(vm.messages.successText, {model: vm.model.toLowerCase(), name: name}),
                    type: 'success',
                }).then(function() {
                    // In certain cases we want to call a function of another controller.
                    if (vm.callback) {
                        // Call the given function.
                        vm.callback();
                    } else {
                        if (Settings.page.previousState) {
                            // Check if we're coming from another page.
                            $state.go(Settings.page.previousState.state, Settings.page.previousState.params);
                        } else {
                            // Otherwise just go to the parent state.
                            $state.go($state.current.parent);
                        }
                    }
                });
            }
        });
    }
}
