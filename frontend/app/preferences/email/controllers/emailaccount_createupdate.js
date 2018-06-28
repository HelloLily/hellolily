angular.module('app.preferences').config(accountConfig);

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
                var configs = emailAccount.shared_email_configs;

                if (configs.length) {
                    for (i = 0; i < configs.length; i++) {
                        if (i > 0) {
                            filterquery += ' OR ';
                        }

                        filterquery += 'id: ' + configs[i].user;
                    }

                    return User.search({filterquery: filterquery, size: 100}).$promise;
                }

                return [];
            }],
        },
    });
}

angular.module('app.preferences').controller('EmailAccountCreateController', EmailAccountUpdateController);

EmailAccountUpdateController.$inject = ['$scope', '$state', '$stateParams', '$timeout', 'HLForms', 'HLSearch',
    'HLUtils', 'EmailAccount', 'emailAccount', 'User', 'sharedWithUsers'];
function EmailAccountUpdateController($scope, $state, $stateParams, $timeout, HLForms, HLSearch,
    HLUtils, EmailAccount, emailAccount, User, sharedWithUsers) {
    var vm = this;

    vm.emailAccount = emailAccount;
    vm.onlyNew = null;
    vm.privacyOptions = EmailAccount.getPrivacyOptions();
    vm.privacyOverride = EmailAccount.PUBLIC;
    vm.shareAdditions = [];

    vm.saveEmailAccount = saveEmailAccount;
    vm.cancelEditing = cancelEditing;
    vm.refreshUsers = refreshUsers;
    vm.addSharedUsers = addSharedUsers;
    vm.getConfigUsers = getConfigUsers;

    activate();

    ////

    function activate() {
        $timeout(() => {
            // Focus the first input on page load.
            angular.element('input')[0].focus();
            $scope.$apply();
        });

        if (sharedWithUsers.objects) {
            for (let i = 0; i < sharedWithUsers.objects.length; i++) {
                vm.emailAccount.shared_email_configs[i].user = sharedWithUsers.objects[i];
            }
        }

        if (!vm.emailAccount.color) {
            vm.emailAccount.color = HLUtils.getColorCode(vm.emailAccount.email_address);
        }
    }

    function cancelEditing() {
        EmailAccount.cancel({id: vm.emailAccount.id}).$promise.then(response => {
            currentUser.displayEmailWarning = false;

            $state.go('base.preferences.emailaccounts', {}, {reload: true});
        });
    }

    function saveEmailAccount(form) {
        var config;
        var args;
        var cleanedAccount;

        if (vm.shareAdditions.length) {
            addSharedUsers();
        }

        cleanedAccount = angular.copy(vm.emailAccount);

        // Loop through users and add them to the shared email config.
        for (config of cleanedAccount.shared_email_configs) {
            config.user = config.user.id;
        }

        args = {
            id: cleanedAccount.id,
            from_name: cleanedAccount.from_name,
            label: cleanedAccount.label,
            privacy: cleanedAccount.privacy,
            shared_email_configs: cleanedAccount.shared_email_configs,
            color: cleanedAccount.color,
        };

        if (vm.emailAccount.only_new === null && vm.onlyNew !== null) {
            args.only_new = vm.onlyNew;
        }

        HLForms.blockUI();
        HLForms.clearErrors(form);

        if (cleanedAccount.id) {
            // If there's an ID set it means we're dealing with an existing account, so update it. Also newly added
            // email accounts already have an ID.
            EmailAccount.patch(args).$promise.then(() => {
                User.me().$promise.then(user => {
                    toastr.success('I\'ve updated the email account for you!', 'Done');

                    // Update global user variable.
                    currentUser.displayEmailWarning = false;
                    $state.go('base.preferences.emailaccounts', {}, {reload: true});
                });
            }, response => {
                _handleBadResponse(response, form);
            });
        }
    }

    function _handleBadResponse(response, form) {
        HLForms.setErrors(form, response.data);

        toastr.error('Uh oh, there seems to be a problem', 'Oops!');
    }

    function addSharedUsers() {
        var user;

        for (user of vm.shareAdditions) {
            vm.emailAccount.shared_email_configs.push({
                user: user,
                privacy: vm.privacyOverride,
                email_account: vm.emailAccount.id,
            });
        }

        vm.shareAdditions = [];
    }

    function getConfigUsers() {
        var users = [];
        var config;

        for (config of vm.emailAccount.shared_email_configs) {
            users.push(config.user);
        }

        return users;
    }

    function refreshUsers(query) {
        var usersPromise;
        var extraQuery = ' AND NOT id:' + currentUser.id;

        if (vm.users && vm.users.length && !query.length) {
            // Clear the previous list so we can retreive the whole list again.
            vm.users = null;
        }

        if (!vm.users || query.length) {
            usersPromise = HLSearch.refreshList(query, 'User', 'is_active:true' + extraQuery, 'full_name', 'full_name');

            if (usersPromise) {
                usersPromise.$promise.then(data => {
                    vm.users = data.objects;
                });
            }
        }
    }
}
