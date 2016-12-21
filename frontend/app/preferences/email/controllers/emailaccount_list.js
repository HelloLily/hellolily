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
        },
    });
}

angular.module('app.preferences').controller('PreferencesEmailAccountList', PreferencesEmailAccountList);

PreferencesEmailAccountList.$inject = ['$compile', '$filter', '$http', '$scope', '$templateCache', 'EmailAccount',
    'HLResource', 'User', 'user'];
function PreferencesEmailAccountList($compile, $filter, $http, $scope, $templateCache, EmailAccount,
                                     HLResource, User, user) {
    var vm = this;

    vm.ownedAccounts = [];
    vm.sharedAccounts = [];
    vm.publicAccounts = [];
    vm.currentUser = user;

    vm.activate = activate;
    vm.followShared = followShared;
    vm.hideShared = hideShared;
    vm.loadAccounts = loadAccounts;
    vm.openShareAccountModal = openShareAccountModal;
    vm.togglePrimaryAccount = togglePrimaryAccount;

    activate();

    ////////

    function activate() {
        loadAccounts();
    }

    // Get relevant accounts.
    function loadAccounts() {
        // Accounts owned.
        EmailAccount.query({owner: vm.currentUser.id}, function(accountData) {
            vm.ownedAccounts = accountData.results;

            // Get public accounts.
            EmailAccount.query({privacy: EmailAccount.PUBLIC}, function(publicAccountData) {
                if (publicAccountData.results.length) {
                    // Filter out own public email accounts.
                    vm.publicAccounts = $filter('xor')(publicAccountData.results, accountData.results);
                }

                publicAccountData.results.forEach(function(account) {
                    _checkHiddenState(account);
                });
            });
        });

        // Accounts shared with user.
        EmailAccount.query({shared_with_users__id: vm.currentUser.id}, function(data) {
            vm.sharedAccounts = data.results;

            data.results.forEach(function(account) {
                _checkHiddenState(account);
            });
        });
    }

    function _checkHiddenState(account) {
        $http.get('/api/messaging/email/shared-email-configurations/?email_account=' + account.id).success(function(d) {
            var isHidden = false;
            if (d.results.length) {
                if (d.results[0].is_hidden) {
                    isHidden = true;
                }
            }

            account.hidden = isHidden;
        });
    }

    function updateSharedEmailSetting(accountId, isHidden) {
        var body = {email_account: accountId};
        if (isHidden) {
            body.is_hidden = true;
        }
        $http.post('/api/messaging/email/shared-email-configurations/', body);
    }

    function followShared(account) {
        account.hidden = false;
        updateSharedEmailSetting(account.id, false);
    }

    function hideShared(account) {
        account.hidden = true;
        updateSharedEmailSetting(account.id, true);
    }

    function openShareAccountModal(emailAccount) {
        vm.currentAccount = emailAccount;

        User.query({}, function(data) {
            vm.users = [];
            // Check if user has the email account already shared.
            angular.forEach(data.results, function(userObject) {
                // Can't share with yourself, so don't include own user.
                if (userObject.id !== vm.currentUser.id) {
                    if (vm.currentAccount.shared_with_users.indexOf(userObject.id) !== -1) {
                        userObject.sharedWith = true;
                    }

                    vm.users.push(userObject);
                }
            });

            swal({
                title: messages.alerts.preferences.shareAccountTitle,
                html: $compile($templateCache.get('preferences/email/controllers/emailaccount_share.html'))($scope),
                showCancelButton: true,
                showCloseButton: true,
            }).then(function(isConfirm) {
                var sharedWithUsers = [];

                if (isConfirm) {
                    // Save updated account information.
                    if (vm.currentAccount.isPublic) {
                        EmailAccount.update({id: vm.currentAccount.id}, vm.currentAccount, function() {
                            swal.close();
                            loadAccounts();
                        });
                    } else {
                        // Get ids of the users to share with.
                        angular.forEach(vm.users, function(userObject) {
                            if (userObject.sharedWith) {
                                sharedWithUsers.push(userObject.id);
                            }
                        });

                        // Push ids to api.
                        EmailAccount.shareWith({id: vm.currentAccount.id}, {shared_with_users: sharedWithUsers}, function() {
                            swal.close();
                            loadAccounts();
                        });
                    }
                }
            }).done();
        });
    }

    function togglePrimaryAccount(emailAccount) {
        var args = {
            id: 'me',
        };

        if (vm.currentUser.primary_email_account && vm.currentUser.primary_email_account.id === emailAccount.id) {
            // Unset primary email account..
            vm.currentUser.primary_email_account = null;
            args.primary_email_account = null;
        } else {
            // Set primary email account.
            vm.currentUser.primary_email_account = emailAccount;
            args.primary_email_account = {id: vm.currentUser.primary_email_account.id};
        }

        HLResource.patch('User', args);
    }
}
