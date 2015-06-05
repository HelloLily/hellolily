angular.module('app.contacts').config(contactsConfig);

contactsConfig.$inject = ['$stateProvider'];
function contactsConfig ($stateProvider) {
    $stateProvider.state('base.contacts.detail', {
        url: '/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'contacts/controllers/detail.html',
                controller: 'ContactDetailController'
            }
        },
        ncyBreadcrumb: {
            label: '{{ contact.name }}'
        },
        resolve: {
            contact: ['ContactDetail', '$stateParams', function (ContactDetail, $stateParams) {
                var contactId = $stateParams.id;
                return ContactDetail.get({id: contactId}).$promise
            }]
        }
    });
}

angular.module('app.contacts').controller('ContactDetailController', ContactDetail);

ContactDetail.$inject = ['$scope', '$stateParams', 'ContactDetail', 'CaseDetail', 'contact'];
function ContactDetail($scope, $stateParams, ContactDetail, CaseDetail, contact) {
    var id = $stateParams.id;

    $scope.contact = contact;

    if ($scope.contact.accounts) {
        $scope.contact.accounts.forEach(function(account) {
            var colleagueList = ContactDetail.query({filterquery: 'NOT(id:' + id + ') AND accounts.id:' + account.id});
            colleagueList.$promise.then(function(colleagues) {
                account.colleagueList = colleagues;
            })
        });
    }

    $scope.conf.pageTitleBig = 'Contact detail';
    $scope.conf.pageTitleSmall = 'the devil is in the details';

    $scope.caseList = CaseDetail.query({filterquery: 'contact:' + id});
    $scope.caseList.$promise.then(function(caseList) {
        $scope.caseList = caseList;
    });
}
