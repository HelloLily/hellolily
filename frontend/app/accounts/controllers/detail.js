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
                return Account.get({id: $stateParams.id}).$promise;
            }],
            caseList: ['Case', '$stateParams', function(Case, $stateParams) {
                return Case.query({filterquery: 'account.id:' + $stateParams.id, sort: 'expires', size: 100}).$promise;
            }],
            contactList: ['Contact', '$stateParams', function(Contact, $stateParams) {
                return Contact.search({filterquery: 'accounts.id:' + $stateParams.id}).$promise;
            }],
            dealList: ['Deal', '$stateParams', function(Deal, $stateParams) {
                return Deal.query({filterquery: 'account.id:' + $stateParams.id, sort: '-created'}).$promise;
            }],
        },
    });
}

angular.module('app.accounts').controller('AccountDetailController', AccountDetailController);

AccountDetailController.$inject = ['HLResource', 'Settings', 'currentAccount', 'caseList', 'contactList', 'dealList'];
function AccountDetailController(HLResource, Settings, currentAccount, caseList, contactList, dealList) {
    var vm = this;

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
        vm.caseList = caseList.objects;
        vm.contactList = contactList.objects;
        vm.dealList = dealList.objects;
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
