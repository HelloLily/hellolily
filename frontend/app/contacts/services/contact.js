angular.module('app.contacts.services').factory('Contact', Contact);

Contact.$inject = ['$resource'];
function Contact($resource) {
    var Contact = $resource(
        '/api/contacts/contact/:id/',
        null,
        {
            update: {
                method: 'PUT',
                params: {
                    id: '@id',
                },
            },
            delete: {
                method: 'DELETE',
            },
            addressOptions: {
                url: '/api/utils/countries/',
                method: 'OPTIONS',
            },
            search: {
                url: '/search/search/?type=contacts_contact&filterquery=:filterquery',
                method: 'GET',
                isArray: true,
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    var objects = [];
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function(obj) {
                            objects.push(obj);
                        });
                    }
                    return objects;
                },
            },
        }
    );

    Contact.create = create;

    //////

    function create() {
        return new Contact({
            salutation: 1, // Default salutation is 'Informal'
            gender: 2, // Default gender is 'Unknown/Other'
            first_name: '',
            preposition: '',
            last_name: '',
            email_addresses: [],
            phone_numbers: [],
            addresses: [],
            tags: [],
            accounts: [],
        });
    }

    return Contact;
}

