angular.module('app.contacts').config(contactsConfig);

contactsConfig.$inject = ['$stateProvider'];
function contactsConfig ($stateProvider) {
    $stateProvider.state('base.contacts.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: function(elem, attr) {
                    return '/contacts/edit/' + elem.id +'/';
                },
                controller: ContactEditController
            }
        },
        ncyBreadcrumb: {
            label: 'Edit'
        }
    });
}

angular.module('app.contacts').controller('ContactEditController', ContactEditController);

ContactEditController.$inject = ['$scope', '$stateParams', 'ContactDetail'];
function ContactEditController ($scope, $stateParams, ContactDetail) {
    var id = $stateParams.id;
    var contactPromise = ContactDetail.get({id: id}).$promise;

    contactPromise.then(function(contact) {
        $scope.contact = contact;
        $scope.conf.pageTitleBig = contact.name;
        $scope.conf.pageTitleSmall = 'change is natural';
        HLSelect2.init();
    });
}
