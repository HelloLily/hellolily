require('ng-file-upload');

angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.user.profile', {
        parent: 'base.preferences.user',
        url: '/profile',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/user/controllers/user_profile.html',
                controller: PreferencesUserProfileController,
                controllerAs: 'vm',
            },
        },
        resolve: {
            user: ['User', (User) => User.me().$promise],
        },
    });
}

angular.module('app.preferences').controller('PreferencesUserProfileController', PreferencesUserProfileController);

PreferencesUserProfileController.$inject = ['$state', '$window', 'HLForms', 'HLUtils', 'Upload', 'user'];
function PreferencesUserProfileController($state, $window, HLForms, HLUtils, Upload, user) {
    const vm = this;

    vm.user = user;

    vm.saveUser = saveUser;
    vm.cancelProfileEditing = cancelProfileEditing;
    vm.notificationsDenied = 'Notification' in window && Notification.permission === 'denied';

    activate();

    //////

    function activate() {
        if (vm.user.profile_picture) {
            vm.user.picture = vm.user.profile_picture;
        }

        if (vm.user.hasOwnProperty('social_media') && vm.user.social_media.length) {
            angular.forEach(vm.user.social_media, profile => {
                vm.user[profile.name] = profile.username;
            });
        }
    }

    function saveUser(form) {
        const formName = '[name="userForm"]';

        // Manually set the fields because Upload.upload doesn't
        // seem to handle Angular resources very well.
        const data = {
            'first_name': vm.user.first_name,
            'last_name': vm.user.last_name,
            'position': vm.user.position,
            'phone_number': vm.user.phone_number,
            'internal_number': vm.user.internal_number ? vm.user.internal_number : '',
        };

        if (vm.user.picture instanceof File || !vm.user.picture) {
            data.picture = vm.user.picture;
        }

        if ('Notification' in window &&
            Notification.permission !== 'granted' &&
            Notification.permission !== 'denied') {
            Notification.requestPermission((permission) => {
                swal.clickConfirm();
            });
            swal({
                title: messages.alerts.notificationPermission.title,
                text: messages.alerts.notificationPermission.text,
                showConfirmButton: false,
                showCloseButton: false,
                showCancelButton: false,
                allowOutsideClick: false,
                allowEscapeKey: false,
                padding: 30,
            }).then(() => {
                saveUserForm(form, formName, data);
            }).done();
        } else {
            saveUserForm(form, formName, data);
        }
    }

    function saveUserForm(form, formName, data) {
        HLUtils.blockUI(formName, true);
        HLForms.clearErrors(form);

        Upload.upload({
            url: 'api/users/me/',
            method: 'PATCH',
            data: data,
        }).then(() => {
            toastr.success(messages.notifications.profileUpdated, messages.notifications.successTitle);
            // Regular state reload isn't enough here, because the picture isn't reloaded.
            // So do a full refresh to show the updated picture.
            $window.location.reload();
        }, response => {
            HLUtils.unblockUI(formName);
            HLForms.setErrors(form, response.data);

            toastr.error(messages.notifications.error, messages.notifications.errorTitle);
        });
    }

    function cancelProfileEditing() {
        $state.reload();
    }
}
