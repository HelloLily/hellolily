angular.module('app.contacts').config(contactsConfig);

contactsConfig.$inject = ['$stateProvider'];
function contactsConfig ($stateProvider) {
    $stateProvider.state('base.contacts.detail.delete', {
        url: '/delete',
        views: {
            '@': {
                controller: ContactDeleteController
            }
        }
    });
}

angular.module('app.contacts').controller('ContactDeleteController', ContactDeleteController);

ContactDeleteController.$inject = ['$state', '$stateParams', 'ContactTest'];
function ContactDeleteController($state, $stateParams, ContactTest) {
    var id = $stateParams.id;

    ContactTest.delete({
        id:id
    }, function() {  // On success
        $state.go('base.contacts');
    }, function(error) {  // On error
        // Error notification needed
        $state.go('base.contacts');
    });
}
