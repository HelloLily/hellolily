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
                return EmailAccount.query({shared_with_users__id: user.id}).$promise;
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

    vm.publicPrivacy = EmailAccount.PUBLIC;

    vm.activate = activate;
    vm.toggleHidden = toggleHidden;
    vm.loadAccounts = loadAccounts;
    vm.openShareAccountModal = openShareAccountModal;
    vm.setPrimaryEmailAccount = setPrimaryEmailAccount;
    vm.removeFromList = removeFromList;
    vm.addSharedUsers = addSharedUsers;
    vm.removeSharedUser = removeSharedUser;
    vm.refreshUsers = refreshUsers;

    activate();

    ////////

    function activate() {
        loadAccounts();
    }

    function loadAccounts() {
        var sharedAccounts = sharedWithAccounts.results;

        ownedAccounts.results.forEach(function(account) {
            _checkHiddenState(account);
        });

        vm.ownedAccounts = ownedAccounts.results;

        if (publicAccounts.results.length) {
            // Combine arrays and filter out already retrieved accounts.
            sharedAccounts = $filter('concat')(publicAccounts.results, sharedAccounts);
            sharedAccounts = $filter('unique')(sharedAccounts, 'id');
        }

        sharedAccounts.forEach(function(account) {
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
            is_hidden: isHidden || false,
        };

        HLResource.patch('SharedEmailConfig', args, 'email account');
    }

    function toggleHidden(account) {
        _updateSharedEmailSetting(account.id, account.is_hidden);
    }

    function openShareAccountModal(account) {
        var i;
        var sharedWithUsers = account.shared_with_users;
        var filterObject = {
            filterquery: '',
        };

        vm.currentAccount = account;

        if (sharedWithUsers.length) {
            for (i = 0; i < sharedWithUsers.length; i++) {
                if (i > 0) {
                    filterObject.filterquery += ' OR ';
                }

                filterObject.filterquery += 'id: ' + sharedWithUsers[i];
            }
        }

        User.search(filterObject).$promise.then(function(data) {
            if (filterObject.filterquery) {
                vm.sharedWithUsers = data.objects;
            }

            swal({
                html: $compile($templateCache.get('preferences/email/controllers/emailaccount_share.html'))($scope),
                showCancelButton: true,
                showCloseButton: true,
            }).then(function(isConfirm) {
                var args = {
                    id: account.id,
                    shared_with_users: [],
                };

                if (vm.shareAdditions.length) {
                    addSharedUsers();
                }

                if (isConfirm) {
                    // // Get IDs of the users to share with.
                    angular.forEach(vm.sharedWithUsers, function(userObject) {
                        args.shared_with_users.push(userObject.id);
                    });

                    HLResource.patch('EmailAccount', args).$promise.then(function() {
                        account.shared_with_users = args.shared_with_users;
                        swal.close();
                    });
                }
            }).done();
        });
    }

    function addSharedUsers() {
        vm.sharedWithUsers = vm.sharedWithUsers.concat(vm.shareAdditions);
        vm.shareAdditions = [];
    }

    function removeSharedUser(sharedUser) {
        var index = vm.sharedWithUsers.indexOf(sharedUser);
        vm.sharedWithUsers.splice(index, 1);
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
        var args = {
            id: 'me',
            primary_email_account: {
                id: account.id,
            },
        };

        HLResource.patch('User', args);
    }
}
