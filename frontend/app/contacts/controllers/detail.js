angular.module('app.contacts').config(contactsConfig);

contactsConfig.$inject = ['$stateProvider'];
function contactsConfig($stateProvider) {
    $stateProvider.state('base.contacts.detail', {
        url: '/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'contacts/controllers/detail.html',
                controller: 'ContactDetailController',
            },
        },
        ncyBreadcrumb: {
            label: '{{ contact.full_name }}',
        },
        resolve: {
            currentContact: ['Contact', '$stateParams', function(Contact, $stateParams) {
                var contactId = $stateParams.id;
                return Contact.get({id: contactId}).$promise;
            }],
        },
    });
}

angular.module('app.contacts').controller('ContactDetailController', ContactDetailController);

ContactDetailController.$inject = ['$scope', '$stateParams', 'Settings', 'Contact', 'Case', 'Deal', 'currentContact'];
function ContactDetailController($scope, $stateParams, Settings, Contact, Case, Deal, currentContact) {
    var id = $stateParams.id;

    $scope.contact = currentContact;
    $scope.height = 200;

    Settings.page.setAllTitles('detail', currentContact.full_name);

    if ($scope.contact.accounts) {
        $scope.contact.accounts.forEach(function(account) {
            var colleagueList = Contact.search({filterquery: 'NOT(id:' + id + ') AND accounts.id:' + account.id});
            colleagueList.$promise.then(function(response) {
                account.colleagueList = response.objects;
            });
        });

        if ($scope.contact.accounts.length >= 2) {
            $scope.height = 91;
        }
    }

    $scope.caseList = Case.query({filterquery: 'contact:' + id, sort: '-created', size: 100});
    $scope.caseList.$promise.then(function(caseList) {
        $scope.caseList = caseList;
    });

    $scope.dealList = Deal.query({filterquery: 'contact:' + id, sort: '-created'});
    $scope.dealList.$promise.then(function(dealList) {
        $scope.dealList = dealList;
    });
}
