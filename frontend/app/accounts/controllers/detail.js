/**
 * Router definition.
 */
angular.module('app.accounts').config(accountConfig);

accountConfig.$inject = ['$stateProvider'];
function accountConfig($stateProvider) {
    $stateProvider.state('base.accounts.detail', {
        parent: 'base.accounts',
        url: '/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'accounts/controllers/detail.html',
                controller: AccountDetailController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: '{{ account.name }}',
        },
        resolve: {
            currentAccount: ['Account', '$stateParams', function(Account, $stateParams) {
                var accountId = $stateParams.id;
                return Account.get({id: accountId}).$promise;
            }],
        },
    });
}

angular.module('app.accounts').controller('AccountDetailController', AccountDetailController);

AccountDetailController.$inject = ['$stateParams', 'Case', 'Contact', 'Deal', 'HLResource', 'Settings', 'currentAccount'];
function AccountDetailController($stateParams, Case, Contact, Deal, HLResource, Settings, currentAccount) {
    var vm = this;
    var id = $stateParams.id;

    Settings.page.setAllTitles('detail', currentAccount.name);
    Settings.page.toolbar.data = {
        model: 'Account',
        object: currentAccount,
        field: 'name',
        updateCallback: updateModel,
    };

    vm.account = currentAccount;

    vm.updateModel = updateModel;

    activate();

    ////

    function activate() {
        vm.caseList = Case.query({filterquery: 'account.id:' + id, sort: '-created', size: 100});
        vm.caseList.$promise.then(function(caseList) {
            vm.caseList = caseList;
        });

        vm.dealList = Deal.query({filterquery: 'account.id:' + id, sort: '-created'});
        vm.dealList.$promise.then(function(dealList) {
            vm.dealList = dealList;
        });

        vm.contactList = Contact.search({filterquery: 'accounts.id:' + id, size: 100});
        vm.contactList.$promise.then(function(results) {
            vm.contactList = results.objects;
        });
    }

    function updateModel(data, field) {
        var args = HLResource.createArgs(data, field, vm.account);

        if (field === 'twitter') {
            args = {
                id: vm.account.id,
                social_media: [args],
            };
        }

        if (field === 'name') {
            Settings.page.setAllTitles('detail', data);
        }

        return HLResource.patch('Account', args).$promise;
    }
}
