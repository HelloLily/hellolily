angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.user.security', {
        url: '/security',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/user/controllers/security.html',
                controller: PreferencesUserSecurityController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'security',
        },
        resolve: {
            twoFactor: ['TwoFactor', TwoFactor => TwoFactor.query().$promise],
            userSession: ['UserSession', UserSession => UserSession.query().$promise],
        },
    });
}

angular.module('app.preferences').controller('PreferencesUserSecurityController', PreferencesUserSecurityController);

PreferencesUserSecurityController.$inject = ['$compile', '$scope', '$state', '$templateCache', 'TwoFactor', 'UserSession', 'twoFactor', 'userSession'];
function PreferencesUserSecurityController($compile, $scope, $state, $templateCache, TwoFactor, UserSession, twoFactor, userSession) {
    const vm = this;

    vm.twoFactor = twoFactor;
    vm.userSessions = userSession.results;
    vm.messages = messages.alerts.preferences.twoFactorAuth;

    vm.showBackupPhoneNumbers = showBackupPhoneNumbers;
    vm.openRemoveBackupPhoneNumberModal = openRemoveBackupPhoneNumberModal;
    vm.showBackupTokens = showBackupTokens;
    vm.twoFactorDisabled = twoFactorDisabled;
    vm.openEndSessionModal = openEndSessionModal;

    activate();

    //////

    function activate() {}

    function showBackupPhoneNumbers() {
        swal({
            title: '',
            html: $compile($templateCache.get('preferences/user/controllers/security_backup_phone_numbers.html'))($scope),
            showCloseButton: true,
            confirmButtonText: 'Add another',
        }).then(() => {
            window.location.href = '/two-factor/backup/phone/register/';
        });
    }

    function openRemoveBackupPhoneNumberModal(phoneNumber) {
        swal({
            title: vm.messages.removeBackupPhoneNumber.title,
            html: vm.messages.removeBackupPhoneNumber.html,
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#f3565d',
            confirmButtonText: vm.messages.removeBackupPhoneNumber.confirmButtonText,
            preConfirm: () => {
                swal.enableLoading();

                return new Promise(resolve => {
                    TwoFactor.remove_phone({id: phoneNumber.id}, () => {
                        // Delete was successful, so continue.
                        resolve();
                    }, error => {
                        // Otherwise show error alert.
                        swal({
                            title: vm.messages.removeBackupPhoneNumber.error.title,
                            html: vm.messages.removeBackupPhoneNumber.error.html,
                            type: 'error',
                        });
                    });
                });
            },
        }).then(isConfirm => {
            if (isConfirm) {
                toastr.success(messages.notifications.twoFactorPhoneRemoved, messages.notifications.successTitle);
                $state.reload();
            }
        }).done();
    }

    function showBackupTokens() {
        swal({
            title: '',
            html: $compile($templateCache.get('preferences/user/controllers/security_backup_tokens.html'))($scope),
            showCloseButton: true,
            confirmButtonText: messages.alerts.twoFactorAuth.backup.confirmButtonText,
        }).then(isConfirm => {
            if (isConfirm) {
                TwoFactor.regenerate_tokens(response => {
                    vm.twoFactor.backup_tokens = response;
                    toastr.success(messages.notifications.twoFactorNewTokens, messages.notifications.successTitle);
                });
            }
        });
    }

    function twoFactorDisabled() {
        $state.reload();
    }

    function openEndSessionModal(session) {
        swal({
            title: vm.messages.endSession.title,
            html: vm.messages.endSession.html,
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#f3565d',
            confirmButtonText: vm.messages.endSession.confirmButtonText,
            preConfirm: () => {
                swal.enableLoading();

                return new Promise(resolve => {
                    UserSession.delete({session_key: session.session_key}, () => {
                        // Delete was successful, so continue.
                        resolve();
                    }, error => {
                        // Otherwise show error alert.
                        swal({
                            title: vm.messages.endSession.error.title,
                            html: vm.messages.endSession.error.html,
                            type: 'error',
                        });
                    });
                });
            },
        }).then(isConfirm => {
            if (isConfirm) {
                toastr.success(messages.notifications.sessionEnded, messages.notifications.sessionEndedTitle);
                $state.reload();
            }
        }).done();
    }
}
