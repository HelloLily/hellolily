angular.module('app.preferences').config(emailPreferencesStates);

emailPreferencesStates.$inject = ['$stateProvider'];
function emailPreferencesStates($stateProvider) {
    $stateProvider.state('base.preferences.emailaccounts', {
        url: '/emailaccounts',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/controllers/emailaccount_list.html',
                controller: PreferencesEmailAccountList,
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: 'Email Account'
        },
        resolve: {
            ownedAccounts: ['EmailAccount', function (EmailAccount) {
                return EmailAccount.query({owner: currentUser.id}).$promise;
            }],
            sharedAccounts: ['EmailAccount', function (EmailAccount) {
                return EmailAccount.query({shared_with_users__id: currentUser.id}).$promise;
            }],
            publicAccounts: ['EmailAccount', function (EmailAccount) {
                return EmailAccount.query({public: "True"}).$promise;
            }],
            user: ['User', function (User) {
                return User.me().$promise;
            }]
        }
    });
}

angular.module('app.preferences').controller('PreferencesEmailAccountList', PreferencesEmailAccountList);

PreferencesEmailAccountList.$inject =['$modal', 'EmailAccount', 'User', 'ownedAccounts', 'sharedAccounts', 'publicAccounts', 'user'];
function PreferencesEmailAccountList($modal, EmailAccount, User, ownedAccounts, sharedAccounts, publicAccounts, user) {

    var vm = this;
    vm.ownedAccounts = ownedAccounts;
    vm.sharedAccounts = sharedAccounts;
    vm.publicAccounts = publicAccounts;
    vm.currentUser = user;
    vm.activate = activate;
    vm.deleteAccount = deleteAccount;
    vm.openShareAccountModal = openShareAccountModal;
    vm.makePrimaryAccount = makePrimaryAccount;

    activate();

    ////////

    function activate() {}

    // Get relevant accounts
    function loadAccounts() {
        // Accounts owned
        EmailAccount.query({owner: vm.currentUser.id}, function(data) {
            vm.ownedAccounts = data;
        });

        // Accounts shared with user
        EmailAccount.query({shared_with_users__id: vm.currentUser.id}, function(data) {
            vm.sharedAccounts = data;
        });

        // Accounts public
        EmailAccount.query({public: "True"}, function(data) {
            vm.publicAccounts = data;
        });
    }

    function deleteAccount (accountId) {
        if (confirm('sure to delete?')) {
            EmailAccount.delete({id: accountId}, function() {
                // Reload accounts
                loadAccounts();
            });
        }
    }

    function openShareAccountModal (emailAccount) {
        var modalInstance = $modal.open({
            templateUrl: 'preferences/controllers/emailaccount_share.html',
            controller: 'EmailAccountShareModalController',
            size: 'lg',
            resolve: {
                currentAccount: function() {
                    return emailAccount;
                }
            }
        });

        modalInstance.result.then(function () {
            loadAccounts();
        }, function() {
            loadAccounts();
        });
    }

    function makePrimaryAccount (emailAccount) {
        vm.currentUser.primary_email_account = emailAccount.id;
        User.update({id: 'me'}, vm.currentUser);
    }
}
