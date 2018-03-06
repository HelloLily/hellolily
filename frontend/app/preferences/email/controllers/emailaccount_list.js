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
            user: ['User', User => User.me().$promise],
            ownedAccounts: ['EmailAccount', 'user', (EmailAccount, user) => {
                return EmailAccount.query({owner: user.id}).$promise;
            }],
            sharedWithAccounts: ['EmailAccount', 'user', (EmailAccount, user) => {
                return EmailAccount.query({sharedemailconfig__user__id: user.id}).$promise;
            }],
            publicAccounts: ['EmailAccount', (EmailAccount) => {
                return EmailAccount.query({privacy: EmailAccount.PUBLIC}).$promise;
            }],
        },
    });
}

angular.module('app.preferences').controller('PreferencesEmailAccountList', PreferencesEmailAccountList);

PreferencesEmailAccountList.$inject = ['$compile', '$filter', '$http', '$scope', '$templateCache', 'EmailAccount',
    'HLResource', 'HLSearch', 'Settings', 'SharedEmailConfig', 'User', 'user', 'ownedAccounts', 'sharedWithAccounts',
    'publicAccounts'];
function PreferencesEmailAccountList($compile, $filter, $http, $scope, $templateCache, EmailAccount,
    HLResource, HLSearch, Settings, SharedEmailConfig, User, user, ownedAccounts, sharedWithAccounts, publicAccounts) {
    const vm = this;

    Settings.page.setAllTitles('list', 'email accounts');

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

        vm.publicAccountTooltip = sprintf(messages.tooltips.emailAccountPublicTooltip, {company: currentUser.company});
    }

    function loadAccounts() {
        let sharedAccounts = [];
        let filteredPublicAccounts = [];

        ownedAccounts.results.map((account) => {
            _checkHiddenState(account);
        });

        vm.ownedAccounts = ownedAccounts.results;

        for (let publicAccount of publicAccounts.results) {
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
        SharedEmailConfig.get({id: account.id}).$promise.then(response => {
            let isHidden = false;

            if (response.results.length && response.results[0].is_hidden) {
                isHidden = true;
            }

            account.is_hidden = isHidden;
        });
    }

    function _updateSharedEmailSetting(accountId, isHidden) {
        const args = {
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
        const configs = account.shared_email_configs;
        const filterObject = {
            filterquery: '',
            size: 50,
        };

        vm.emailAccount = account;

        if (configs.length) {
            for (let i = 0; i < configs.length; i++) {
                if (i > 0) {
                    filterObject.filterquery += ' OR ';
                }

                filterObject.filterquery += 'id: ' + configs[i].user;
            }
        }

        User.search(filterObject).$promise.then(data => {
            if (filterObject.filterquery) {
                if (data.objects) {
                    for (let i = 0; i < data.objects.length; i++) {
                        for (let j = 0; j < vm.emailAccount.shared_email_configs.length; j++) {
                            if (vm.emailAccount.shared_email_configs[j].user === data.objects[i].id) {
                                vm.emailAccount.shared_email_configs[j].user = data.objects[i];
                            }
                        }
                    }
                }
            }

            swal({
                html: $compile($templateCache.get('preferences/email/controllers/emailaccount_share.html'))($scope),
                showCancelButton: true,
                showCloseButton: true,
            }).then(isConfirm => {
                const args = {
                    id: vm.emailAccount.id,
                    shared_email_configs: vm.emailAccount.shared_email_configs,
                };

                if (vm.shareAdditions.length) {
                    addSharedUsers();
                }

                if (isConfirm) {
                    // Loop through users and add them to the shared email config.
                    for (let config of args.shared_email_configs) {
                        config.user = config.user.id;
                    }

                    HLResource.patch('EmailAccount', args).$promise.then(response => {
                        const emailConfigs = [];

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
        for (let sharedUser of vm.shareAdditions) {
            vm.emailAccount.shared_email_configs.push({
                user: sharedUser,
                privacy: vm.privacyOverride,
                email_account: vm.emailAccount.id,
            });
        }

        vm.shareAdditions = [];
    }

    function getConfigUsers() {
        const users = [];

        for (let config of vm.emailAccount.shared_email_configs) {
            users.push(config.user);
        }

        return users;
    }

    function refreshUsers(query) {
        const extraQuery = ` AND NOT id:${currentUser.id}`;

        if (vm.users && vm.users.length && !query.length) {
            // Clear the previous list so we can retreive the whole list again.
            vm.users = null;
        }

        if (!vm.users || query.length) {
            const usersPromise = HLSearch.refreshList(query, 'User', 'is_active:true' + extraQuery, 'full_name', 'full_name');

            if (usersPromise) {
                usersPromise.$promise.then(data => {
                    vm.users = data.objects;
                });
            }
        }
    }

    function removeFromList(account) {
        const index = vm.ownedAccounts.indexOf(account);
        vm.ownedAccounts.splice(index, 1);
        $scope.$apply();
    }

    function setPrimaryEmailAccount(account) {
        if (vm.primaryAccount !== account.id) {
            const args = {
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
            account.shared_email_configs.map(config => {
                if (config.user === user.id && config.privacy === EmailAccount.PUBLIC) {
                    fullAccess = true;
                }
            });
        }

        return fullAccess;
    }
}
