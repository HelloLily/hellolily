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
                url: '/search/search/?type=contacts_contact',
                method: 'GET',
                transformResponse: function(response) {
                    var data = angular.fromJson(response);
                    return {
                        contacts: data.hits,
                        total: data.total,
                    };
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

