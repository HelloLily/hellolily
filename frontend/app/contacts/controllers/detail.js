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
            label: '{{ contact.name }}',
        },
        resolve: {
            contact: ['ContactDetail', '$stateParams', function(ContactDetail, $stateParams) {
                var contactId = $stateParams.id;
                return ContactDetail.get({id: contactId}).$promise;
            }],
        },
    });
}

angular.module('app.contacts').controller('ContactDetailController', ContactDetailController);

ContactDetailController.$inject = ['$scope', '$stateParams', 'Settings', 'ContactDetail', 'CaseDetail', 'contact', 'Deal'];
function ContactDetailController($scope, $stateParams, Settings, ContactDetail, CaseDetail, contact, Deal) {
    var id = $stateParams.id;

    $scope.contact = contact;
    $scope.height = 300;

    Settings.page.setAllTitles('detail', contact.name);

    if ($scope.contact.accounts) {
        $scope.contact.accounts.forEach(function(account) {
            var colleagueList = ContactDetail.query({filterquery: 'NOT(id:' + id + ') AND accounts.id:' + account.id});
            colleagueList.$promise.then(function(colleagues) {
                account.colleagueList = colleagues;
            });
        });

        if ($scope.contact.accounts.length >= 2) {
            $scope.height = 91;
        }
    }

    $scope.caseList = CaseDetail.query({filterquery: 'contact:' + id, sort: '-created'});
    $scope.caseList.$promise.then(function(caseList) {
        $scope.caseList = caseList;
    });

    $scope.dealList = Deal.query({filterquery: 'contact:' + id, sort: '-created'});
    $scope.dealList.$promise.then(function(dealList) {
        $scope.dealList = dealList;
    });

}
