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

PreferencesEmailAccountList.$inject = ['$compile', '$http', '$scope', '$templateCache', 'EmailAccount', 'User', 'user'];
function PreferencesEmailAccountList($compile, $http, $scope, $templateCache, EmailAccount, User, user) {
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
        EmailAccount.query({owner: vm.currentUser.id}, function(data) {
            vm.ownedAccounts = data.results;
        });

        function checkHiddenState(account) {
            $http.get('/api/messaging/email/shared_email_config/?email_account=' + account.id).success(function(d) {
                var isHidden = false;
                if (d.results.length) {
                    if (d.results[0].is_hidden) {
                        isHidden = true;
                    }
                }
                account.hidden = isHidden;
            });
        }

        // Accounts shared with user.
        EmailAccount.query({shared_with_users__id: vm.currentUser.id}, function(data) {
            vm.sharedAccounts = data.results;
            data.results.forEach(function(account) {
                checkHiddenState(account);
            });
        });

        // Accounts public.
        EmailAccount.query({public: 'True'}, function(data) {
            vm.publicAccounts = data.results;
            data.results.forEach(function(account) {
                checkHiddenState(account);
            });
        });
    }

    function updateSharedEmailSetting(accountId, isHidden) {
        var body = {email_account: accountId};
        if (isHidden) {
            body.is_hidden = true;
        }
        $http.post('/api/messaging/email/shared_email_config/', body);
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
                    if (vm.currentAccount.public) {
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
        if (vm.currentUser.primary_email_account === emailAccount.id) {
            // Unset primary email account..
            vm.currentUser.primary_email_account = null;
        } else {
            // Set primary email account.
            vm.currentUser.primary_email_account = emailAccount.id;
        }
        User.update({id: 'me'}, vm.currentUser);
    }
}
