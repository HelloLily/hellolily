angular.module('app.contacts.services').factory('ContactTest', ContactTest);

ContactTest.$inject = ['$resource'];
function ContactTest($resource) {
    var _contactTest = $resource(
        '/api/contacts/:id/',
        {},
        {
            query: {
                isArray: false,
            },
        }
    );

    return _contactTest;
}
