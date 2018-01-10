/**
 * Router definition.
 */
angular.module('app.accounts').config(accountConfig);

accountConfig.$inject = ['$stateProvider'];
function accountConfig($stateProvider) {
    $stateProvider.state('base.accounts.detail', {
        parent: 'base.accounts',
        url: '/{id:int}',
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
            currentAccount: ['Account', '$stateParams', (Account, $stateParams) => {
                return Account.get({id: $stateParams.id}).$promise;
            }],
            caseList: ['Case', '$stateParams', (Case, $stateParams) => {
                return Case.search({filterquery: 'account.id:' + $stateParams.id, sort: 'expires', size: 250}).$promise;
            }],
            contactList: ['Contact', '$stateParams', (Contact, $stateParams) => {
                return Contact.search({filterquery: 'accounts.id:' + $stateParams.id, size: 50}).$promise;
            }],
            dealList: ['Deal', '$stateParams', (Deal, $stateParams) => {
                return Deal.search({filterquery: 'account.id:' + $stateParams.id, sort: '-next_step_date', size: 250}).$promise;
            }],
        },
    });
}

angular.module('app.accounts').controller('AccountDetailController', AccountDetailController);

AccountDetailController.$inject = ['Account', 'Settings', 'currentAccount', 'caseList', 'contactList', 'dealList'];
function AccountDetailController(Account, Settings, currentAccount, caseList, contactList, dealList) {
    const vm = this;

    Settings.page.setAllTitles('detail', currentAccount.name);
    Settings.page.toolbar.data = {
        model: 'Account',
        object: currentAccount,
        field: 'name',
        updateCallback: updateModel,
        formName: 'accountHeaderForm',
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
        return Account.updateModel(data, field, vm.account);
    }
}
