angular.module('app.contacts.services').factory('ContactTest', ContactTest);

ContactTest.$inject = ['$resource'];
function ContactTest ($resource) {
    return $resource('/api/contacts/contact/:id/');
}
