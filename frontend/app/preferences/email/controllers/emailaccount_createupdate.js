angular.module('app.accounts').config(accountConfig);

accountConfig.$inject = ['$stateProvider'];
function accountConfig($stateProvider) {
    $stateProvider.state('base.preferences.emailaccounts.create', {
        url: '/create',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/email/controllers/emailaccount_form.html',
                controller: EmailAccountUpdateController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Create',
        },
        resolve: {
            emailAccount: function() {
                return {};
            },
            sharedWithUsers: function() {
                return [];
            },
        },
    });

    $stateProvider.state('base.preferences.emailaccounts.setup.create', {
        url: '/:id',
        views: {
            '@': {
                templateUrl: 'preferences/email/controllers/emailaccount_form.html',
                controller: EmailAccountUpdateController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Setup',
        },
        resolve: {
            emailAccount: ['EmailAccount', '$stateParams', function(EmailAccount, $stateParams) {
                return EmailAccount.get({id: $stateParams.id}).$promise;
            }],
            sharedWithUsers: function() {
                return [];
            },
        },
    });

    $stateProvider.state('base.preferences.emailaccounts.edit', {
        url: '/edit/{id:[0-9]{1,}}',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/email/controllers/emailaccount_form.html',
                controller: EmailAccountUpdateController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Edit',
        },
        resolve: {
            emailAccount: ['EmailAccount', '$stateParams', function(EmailAccount, $stateParams) {
                return EmailAccount.get({id: $stateParams.id}).$promise;
            }],
            sharedWithUsers: ['User', 'emailAccount', function(User, emailAccount) {
                var i;
                var filterquery = '';
                var sharedWithUsers = emailAccount.shared_with_users;

                if (sharedWithUsers.length) {
                    for (i = 0; i < sharedWithUsers.length; i++) {
                        if (i > 0) {
                            filterquery += ' OR ';
                        }

                        filterquery += 'id: ' + sharedWithUsers[i];
                    }

                    return User.search({filterquery: filterquery}).$promise;
                }

                return [];
            }],
        },
    });
}

angular.module('app.preferences').controller('EmailAccountCreateController', EmailAccountUpdateController);

EmailAccountUpdateController.$inject = ['$scope', '$state', '$stateParams', '$timeout', 'HLForms', 'HLSearch',
    'EmailAccount', 'emailAccount', 'User', 'sharedWithUsers'];
function EmailAccountUpdateController($scope, $state, $stateParams, $timeout, HLForms, HLSearch,
                                      EmailAccount, emailAccount, User, sharedWithUsers) {
    var vm = this;

    vm.emailAccount = emailAccount;
    vm.emailAccount.only_new = false;

    if (sharedWithUsers.objects) {
        vm.emailAccount.shared_with_users = sharedWithUsers.objects;
    }

    vm.privacyOptions = EmailAccount.getPrivacyOptions();
    vm.shareAdditions = [];

    vm.saveEmailAccount = saveEmailAccount;
    vm.cancelEditing = cancelEditing;
    vm.refreshUsers = refreshUsers;
    vm.addSharedUsers = addSharedUsers;
    vm.removeSharedUser = removeSharedUser;

    activate();

    ////

    function activate() {
        $timeout(function() {
            // Focus the first input on page load.
            angular.element('input')[0].focus();
            $scope.$apply();
        });
    }

    function cancelEditing() {
        EmailAccount.cancel({id: vm.emailAccount.id}).$promise.then(function(response) {
            currentUser.displayEmailWarning = false;

            if (response.hasOwnProperty('info')) {
                currentUser.emailAccountStatus = response.info.email_account_status;
                $state.go('base.dashboard', {}, {reload: true});
            } else {
                $state.go('base.preferences.emailaccounts', {}, {reload: true});
            }
        });
    }

    function saveEmailAccount(form) {
        var cleanedAccount;
        var args = {
            id: vm.emailAccount.id,
            from_name: vm.emailAccount.from_name,
            label: vm.emailAccount.label,
            only_new: vm.emailAccount.only_new,
            privacy: vm.emailAccount.privacy,
            shared_with_users: vm.emailAccount.shared_with_users,
        };

        if (vm.shareAdditions.length) {
            addSharedUsers();
        }

        cleanedAccount = HLForms.clean(args);

        HLForms.blockUI();
        HLForms.clearErrors(form);

        if (cleanedAccount.id) {
            // If there's an ID set it means we're dealing with an existing account, so update it.
            EmailAccount.patch(args).$promise.then(function() {
                User.me().$promise.then(function(user) {
                    toastr.success('I\'ve updated the email account for you!', 'Done');

                    // Update global user variable.
                    currentUser.displayEmailWarning = false;
                    currentUser.emailAccountStatus = user.info.email_account_status;

                    if (user.info.email_account_status) {
                        $state.go('base.preferences.emailaccounts', {}, {reload: true});
                    } else {
                        $state.go('base.dashboard', {}, {reload: true});
                    }
                });
            }, function(response) {
                _handleBadResponse(response, form);
            });
        }
    }

    function _handleBadResponse(response, form) {
        HLForms.setErrors(form, response.data);

        toastr.error('Uh oh, there seems to be a problem', 'Oops!');
    }

    function addSharedUsers() {
        vm.emailAccount.shared_with_users = vm.emailAccount.shared_with_users.concat(vm.shareAdditions);
        vm.shareAdditions = [];
    }

    function removeSharedUser(user) {
        var index = vm.emailAccount.shared_with_users.indexOf(user);
        vm.emailAccount.shared_with_users.splice(index, 1);
    }

    function refreshUsers(query) {
        var usersPromise;
        var extraQuery = ' AND NOT id:' + currentUser.id;

        if (!vm.users || query.length) {
            usersPromise = HLSearch.refreshList(query, 'User', 'is_active:true' + extraQuery, 'full_name', 'full_name');

            if (usersPromise) {
                usersPromise.$promise.then(function(data) {
                    vm.users = data.objects;
                });
            }
        }
    }
}
