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
            twoFactor: ['TwoFactor', function(TwoFactor) {
                return TwoFactor.query().$promise;
            }],
            userSession: ['UserSession', function(UserSession) {
                return UserSession.query().$promise;
            }],
        },
    });
}

angular.module('app.preferences').controller('PreferencesUserSecurityController', PreferencesUserSecurityController);

PreferencesUserSecurityController.$inject = ['$compile', '$scope', '$state', '$templateCache', 'Settings',
    'TwoFactor', 'UserSession', 'twoFactor', 'userSession'];
function PreferencesUserSecurityController($compile, $scope, $state, $templateCache, Settings,
    TwoFactor, UserSession, twoFactor, userSession) {
    const vm = this;

    Settings.page.setAllTitles('list', 'security');

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
        }).then(function() {
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
            preConfirm: function() {
                swal.enableLoading();

                return new Promise(function(resolve) {
                    TwoFactor.remove_phone({id: phoneNumber.id},
                        function() {
                            // Delete was successful, so continue.
                            resolve();
                        }, function(error) {
                            // Otherwise show error alert.
                            swal({
                                title: vm.messages.removeBackupPhoneNumber.error.title,
                                html: vm.messages.removeBackupPhoneNumber.error.html,
                                type: 'error',
                            });
                        });
                });
            },
        }).then(function(isConfirm) {
            if (isConfirm) {
                toastr.success('The phone number was successfully removed', 'Done');
                $state.reload();
            }
        }).done();
    }

    function showBackupTokens() {
        swal({
            title: '',
            html: $compile($templateCache.get('preferences/user/controllers/security_backup_tokens.html'))($scope),
            showCloseButton: true,
            confirmButtonText: 'Regenerate',
        }).then(function(isConfirm) {
            if (isConfirm) {
                TwoFactor.regenerate_tokens(function(response) {
                    vm.twoFactor.backup_tokens = response;
                    toastr.success('You now have a new set of backup tokens!', 'Done');
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
            preConfirm: function() {
                swal.enableLoading();

                return new Promise(function(resolve) {
                    UserSession.delete({session_key: session.session_key},
                        function() {
                            // Delete was successful, so continue.
                            resolve();
                        }, function(error) {
                            // Otherwise show error alert.
                            swal({
                                title: vm.messages.endSession.error.title,
                                html: vm.messages.endSession.error.html,
                                type: 'error',
                            });
                        });
                });
            },
        }).then(function(isConfirm) {
            if (isConfirm) {
                toastr.success('The session was successfully ended', 'Session ended!');
                $state.reload();
            }
        }).done();
    }
}
