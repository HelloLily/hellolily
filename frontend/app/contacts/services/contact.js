angular.module('app.contacts.services').factory('Contact', Contact);

Contact.$inject = ['$resource', 'HLForms', 'HLResource'];
function Contact($resource, HLForms, HLResource) {
    var _contact = $resource(
        '/api/contacts/contact/:id/',
        null,
        {
            get: {
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);

                    HLResource.setSocialMediaFields(jsonData);

                    return jsonData;
                },
            },
            query: {
                isArray: false,
            },
            update: {
                method: 'PUT',
                params: {
                    id: '@id',
                },
            },
            patch: {
                method: 'PATCH',
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
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);
                    var objects = [];

                    if (jsonData && jsonData.hits && jsonData.hits.length > 0) {
                        jsonData.hits.forEach(function(obj) {
                            objects.push(obj);
                        });
                    }

                    return {
                        objects: objects,
                        total: jsonData.total,
                    };
                },
            },
        }
    );

    _contact.create = create;
    _contact.getSalutationOptions = getSalutationOptions;
    _contact.getGenderOptions = getGenderOptions;

    function getSalutationOptions() {
        return [
            {id: 0, name: 'Formal'},
            {id: 1, name: 'Informal'},
        ];
    }

    function getGenderOptions() {
        return [
            {id: 0, name: 'Male'},
            {id: 1, name: 'Female'},
            {id: 2, name: 'Unknown/Other'},
        ];
    }

    //////

    function create() {
        return new _contact({
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

    return _contact;
}

