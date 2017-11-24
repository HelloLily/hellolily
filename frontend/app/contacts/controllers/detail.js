angular.module('app.contacts').config(contactsConfig);

contactsConfig.$inject = ['$stateProvider'];
function contactsConfig($stateProvider) {
    $stateProvider.state('base.contacts.detail', {
        parent: 'base.contacts',
        url: '/{id:int}',
        views: {
            '@': {
                templateUrl: 'contacts/controllers/detail.html',
                controller: 'ContactDetailController',
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: '{{ contact.full_name }}',
        },
        resolve: {
            currentContact: ['Contact', '$stateParams', (Contact, $stateParams) => {
                const id = $stateParams.id;
                return Contact.get({id}).$promise;
            }],
            caseList: ['Case', '$stateParams', (Case, $stateParams) => {
                return Case.search({filterquery: 'contact.id:' + $stateParams.id, sort: 'expires', size: 100}).$promise;
            }],
            dealList: ['Deal', '$stateParams', (Deal, $stateParams) => {
                return Deal.search({filterquery: 'contact.id:' + $stateParams.id, sort: '-next_step_date', size: 100}).$promise;
            }],
        },
    });
}

angular.module('app.contacts').controller('ContactDetailController', ContactDetailController);

ContactDetailController.$inject = ['$filter', '$scope', 'Contact', 'Settings', 'currentContact', 'caseList', 'dealList'];
function ContactDetailController($filter, $scope, Contact, Settings, currentContact, caseList, dealList) {
    const vm = this;

    vm.contact = currentContact;
    vm.height = 200;

    vm.updateModel = updateModel;

    Settings.page.setAllTitles('detail', currentContact.full_name);
    Settings.page.toolbar.data = {
        model: 'Contact',
        object: currentContact,
        fields: ['first_name', 'last_name'],
        updateCallback: updateModel,
    };

    activate();

    ////

    function activate() {
        vm.caseList = caseList.objects;
        vm.dealList = dealList.objects;
    }

    $scope.$watchCollection('vm.contact.accounts', () => {
        vm.contact.accounts.forEach(account => {
            account.primary_email_address = $filter('primaryEmail')(account.email_addresses);

            const colleagueList = Contact.search({filterquery: 'NOT(id:' + vm.contact.id + ') AND accounts.id:' + account.id, size: 50});
            colleagueList.$promise.then(response => {
                account.colleagueList = response.objects;
            });
        });

        if (vm.contact.accounts.length >= 2) {
            vm.height = 91;
        }
    });

    function updateModel(data, field) {
        return Contact.updateModel(data, field, vm.contact);
    }
}
