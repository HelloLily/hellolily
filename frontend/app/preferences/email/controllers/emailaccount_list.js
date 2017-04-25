angular.module('app.preferences').config(emailPreferencesStates);

emailPreferencesStates.$inject = ['$stateProvider'];
function emailPreferencesStates($stateProvider) {
    $stateProvider.state('base.preferences.emailaccounts', {
        url: '/emailaccounts',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/email/controllers/emailaccount_list.html',
                controller: PreferencesEmailAccountList,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Email account',
        },
        resolve: {
            user: ['User', function(User) {
                return User.me().$promise;
            }],
            ownedAccounts: ['EmailAccount', 'user', function(EmailAccount, user) {
                return EmailAccount.query({owner: user.id}).$promise;
            }],
            sharedWithAccounts: ['EmailAccount', 'user', function(EmailAccount, user) {
                return EmailAccount.query({sharedemailconfig__user__id: user.id}).$promise;
            }],
            publicAccounts: ['EmailAccount', function(EmailAccount) {
                return EmailAccount.query({privacy: EmailAccount.PUBLIC}).$promise;
            }],
        },
    });
}

angular.module('app.preferences').controller('PreferencesEmailAccountList', PreferencesEmailAccountList);

PreferencesEmailAccountList.$inject = ['$compile', '$filter', '$http', '$scope', '$templateCache', 'EmailAccount',
    'HLResource', 'HLSearch', 'SharedEmailConfig', 'User', 'user', 'ownedAccounts', 'sharedWithAccounts', 'publicAccounts'];
function PreferencesEmailAccountList($compile, $filter, $http, $scope, $templateCache, EmailAccount,
                                     HLResource, HLSearch, SharedEmailConfig, User, user, ownedAccounts, sharedWithAccounts, publicAccounts) {
    var vm = this;

    vm.ownedAccounts = [];
    vm.sharedAccounts = [];
    vm.shareAdditions = [];
    vm.sharedWithUsers = [];
    vm.currentUser = user;

    if (user.primary_email_account) {
        vm.primaryAccount = user.primary_email_account.id;
    }

    vm.privacyOptions = EmailAccount.getPrivacyOptions();
    vm.publicPrivacy = EmailAccount.PUBLIC;
    vm.privacyOverride = EmailAccount.PUBLIC;

    vm.activate = activate;
    vm.toggleHidden = toggleHidden;
    vm.loadAccounts = loadAccounts;
    vm.openShareAccountModal = openShareAccountModal;
    vm.setPrimaryEmailAccount = setPrimaryEmailAccount;
    vm.removeFromList = removeFromList;
    vm.addSharedUsers = addSharedUsers;
    vm.getConfigUsers = getConfigUsers;
    vm.refreshUsers = refreshUsers;
    vm.hasFullAccess = hasFullAccess;

    activate();

    ////////

    function activate() {
        loadAccounts();
    }

    function loadAccounts() {
        var publicAccount;
        var sharedAccounts = [];
        var filteredPublicAccounts = [];

        ownedAccounts.results.map((account) => {
            _checkHiddenState(account);
        });

        vm.ownedAccounts = ownedAccounts.results;

        for (publicAccount of publicAccounts.results) {
            if (publicAccount.owner.id !== vm.currentUser.id) {
                filteredPublicAccounts.push(publicAccount);
            }
        }

        sharedWithAccounts.results.map((account) => {
            if (account.owner.id !== vm.currentUser.id) {
                _checkHiddenState(account);
                sharedAccounts.push(account);
            }
        });

        if (publicAccounts.results.length) {
            // Combine arrays and filter out already retrieved accounts.
            sharedAccounts = $filter('concat')(filteredPublicAccounts, sharedAccounts);
            sharedAccounts = $filter('unique')(sharedAccounts, 'id');
        }

        sharedAccounts.map((account) => {
            _checkHiddenState(account);
        });

        vm.sharedAccounts = sharedAccounts;
    }

    function _checkHiddenState(account) {
        SharedEmailConfig.get({id: account.id}).$promise.then(function(response) {
            var isHidden = false;

            if (response.results.length && response.results[0].is_hidden) {
                isHidden = true;
            }

            account.is_hidden = isHidden;
        });
    }

    function _updateSharedEmailSetting(accountId, isHidden) {
        var args = {
            email_account: accountId,
            user: vm.currentUser.id,
            is_hidden: isHidden || false,
        };

        HLResource.patch('SharedEmailConfig', args, 'email account');
    }

    function toggleHidden(account) {
        _updateSharedEmailSetting(account.id, account.is_hidden);
    }

    function openShareAccountModal(account) {
        var i;
        var configs = account.shared_email_configs;
        var filterObject = {
            filterquery: '',
        };

        vm.emailAccount = account;

        if (configs.length) {
            for (i = 0; i < configs.length; i++) {
                if (i > 0) {
                    filterObject.filterquery += ' OR ';
                }

                filterObject.filterquery += 'id: ' + configs[i].user;
            }
        }

        User.search(filterObject).$promise.then(function(data) {
            if (filterObject.filterquery) {
                if (data.objects) {
                    for (i = 0; i < data.objects.length; i++) {
                        vm.emailAccount.shared_email_configs[i].user = data.objects[i];
                    }
                }
            }

            swal({
                html: $compile($templateCache.get('preferences/email/controllers/emailaccount_share.html'))($scope),
                showCancelButton: true,
                showCloseButton: true,
            }).then(function(isConfirm) {
                var config;
                var args = {
                    id: vm.emailAccount.id,
                    shared_email_configs: vm.emailAccount.shared_email_configs,
                };

                if (vm.shareAdditions.length) {
                    addSharedUsers();
                }

                if (isConfirm) {
                    // Loop through users and add them to the shared email config.
                    for (config of args.shared_email_configs) {
                        config.user = config.user.id;
                    }

                    HLResource.patch('EmailAccount', args).$promise.then(function(response) {
                        var emailConfigs = [];

                        response.shared_email_configs.map((newConfig) => {
                            if (vm.emailAccount.owner.id !== newConfig.user) {
                                emailConfigs.push(newConfig);
                            }
                        });

                        vm.emailAccount.shared_email_configs = emailConfigs;
                        swal.close();
                    });
                }
            }).done();
        });
    }

    function addSharedUsers() {
        var sharedUser;

        for (sharedUser of vm.shareAdditions) {
            vm.emailAccount.shared_email_configs.push({
                user: sharedUser,
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

        if (!vm.users || query.length) {
            usersPromise = HLSearch.refreshList(query, 'User', 'is_active:true' + extraQuery, 'full_name', 'full_name');

            if (usersPromise) {
                usersPromise.$promise.then(function(data) {
                    vm.users = data.objects;
                });
            }
        }
    }

    function removeFromList(account) {
        var index = vm.ownedAccounts.indexOf(account);
        vm.ownedAccounts.splice(index, 1);
        $scope.$apply();
    }

    function setPrimaryEmailAccount(account) {
        var args;

        if (vm.primaryAccount !== account.id) {
            args = {
                id: 'me',
                primary_email_account: {
                    id: account.id,
                },
            };

            vm.primaryAccount = account.id;

            HLResource.patch('User', args);
        }
    }

    function hasFullAccess(account) {
        let fullAccess = false;

        if (account.privacy === EmailAccount.PUBLIC) {
            fullAccess = true;
        } else if (account.shared_email_configs.length) {
            account.shared_email_configs.map((config) => {
                if (config.user === user.id && config.privacy === EmailAccount.PUBLIC) {
                    fullAccess = true;
                }
            });
        }

        return fullAccess;
    }
}
