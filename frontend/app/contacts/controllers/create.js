angular.module('app.contacts').config(contactsConfig);

contactsConfig.$inject = ['$stateProvider'];
function contactsConfig ($stateProvider) {
    $stateProvider.state('base.contacts.create', {
        url: '/create',
        views: {
            '@': {
                templateUrl: 'contacts/create/',
                controller: ContactCreateController
            }
        },
        ncyBreadcrumb: {
            label: 'Create'
        }
    });
    $stateProvider.state('base.contacts.create.fromAccount', {
        url: '/account/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: function(elem, attr){
                    return '/contacts/add/from_account/' + elem.id + '/';
                },
                controller: ContactCreateController
            }
        },
        ncyBreadcrumb:{
            skip: true
        }
    });
}

angular.module('app.contacts').controller('ContactCreateController', ContactCreateController);

ContactCreateController.$inject = ['$scope'];
function ContactCreateController ($scope) {
    $scope.conf.pageTitleBig = 'New contact';
    $scope.conf.pageTitleSmall = 'who did you talk to?';
}
