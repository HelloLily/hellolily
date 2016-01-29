angular.module('app.preferences').config(emailPreferencesStates);

emailPreferencesStates.$inject = ['$stateProvider'];
function emailPreferencesStates($stateProvider) {
    $stateProvider.state('base.preferences.emailaccounts', {
        url: '/emailaccounts',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/controllers/emailaccount_list.html',
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

PreferencesEmailAccountList.$inject = ['$uibModal', 'EmailAccount', 'User', 'user', '$http'];
function PreferencesEmailAccountList($uibModal, EmailAccount, User, user, $http) {
    var vm = this;
    vm.ownedAccounts = [];
    vm.sharedAccounts = [];
    vm.publicAccounts = [];
    vm.currentUser = user;
    vm.activate = activate;
    vm.followShared = followShared;
    vm.hideShared = hideShared;
    vm.deleteAccount = deleteAccount;
    vm.openShareAccountModal = openShareAccountModal;
    vm.makePrimaryAccount = makePrimaryAccount;

    activate();

    ////////

    function activate() {
        loadAccounts();
    }

    // Get relevant accounts
    function loadAccounts() {
        // Accounts owned
        EmailAccount.query({owner: vm.currentUser.id}, function(data) {
            vm.ownedAccounts = data.results;
        });

        function checkHiddenState(account) {
            $http.get('/api/messaging/email/shared_email_config/?email_account=' + account.id).success(function(d) {
                var isHidden = false;
                if (d.length) {
                    if (d[0].is_hidden) {
                        isHidden = true;
                    }
                }
                account.hidden = isHidden;
            });
        }

        // Accounts shared with user
        EmailAccount.query({shared_with_users__id: vm.currentUser.id}, function(data) {
            vm.sharedAccounts = data.results;
            data.results.forEach(function(account) {
                checkHiddenState(account);
            });
        });

        // Accounts public
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

    function deleteAccount(accountId) {
        if (confirm('sure to delete?')) {
            EmailAccount.delete({id: accountId}, function() {
                // Reload accounts
                loadAccounts();
            });
        }
    }

    function openShareAccountModal(emailAccount) {
        var modalInstance = $uibModal.open({
            templateUrl: 'preferences/controllers/emailaccount_share.html',
            controller: 'EmailAccountShareModalController',
            size: 'lg',
            resolve: {
                currentAccount: function() {
                    return emailAccount;
                },
            },
        });

        modalInstance.result.then(function () {
            loadAccounts();
        }, function() {
            loadAccounts();
        });
    }

    function makePrimaryAccount(emailAccount) {
        vm.currentUser.primary_email_account = emailAccount.id;
        User.update({id: 'me'}, vm.currentUser);
    }
}
