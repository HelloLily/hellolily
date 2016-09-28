angular.module('app.contacts.services').factory('Contact', Contact);

Contact.$inject = ['$filter', '$resource', 'HLResource', 'Settings'];
function Contact($filter, $resource, HLResource, Settings) {
    var _contact = $resource(
        '/api/contacts/:id/',
        null,
        {
            get: {
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);

                    HLResource.setSocialMediaFields(jsonData);

                    jsonData.primary_email_address = $filter('primaryEmail')(jsonData.email_addresses);

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
                            obj.primary_email_address = $filter('primaryEmail')(obj.email_addresses);

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
    _contact.updateModel = updateModel;
    _contact.getSalutationOptions = getSalutationOptions;
    _contact.getGenderOptions = getGenderOptions;

    //////

    function create() {
        return new _contact({
            salutation: 1, // Default salutation is 'Informal'
            gender: 2, // Default gender is 'Unknown/Other'
            first_name: '',
            last_name: '',
            email_addresses: [],
            phone_numbers: [],
            addresses: [],
            tags: [],
            accounts: [],
        });
    }

    function updateModel(data, field, contact) {
        var accounts = [];
        var args;
        var patchPromise;

        if (field instanceof Array) {
            args = data;
            args.id = contact.id;
        } else {
            args = HLResource.createArgs(data, field, contact);
        }

        if (field === 'twitter' || field === 'linkedin') {
            args = {
                id: contact.id,
                social_media: [args],
            };
        }

        if (args.hasOwnProperty('accounts')) {
            args.accounts.forEach(function(account) {
                accounts.push(account.id);
            });

            args.accounts = accounts;
        }

        patchPromise = HLResource.patch('Contact', args).$promise;

        patchPromise.then(function(response) {
            if (field instanceof Array) {
                // We're updating the name here, which is an Array when inline editing.
                Settings.page.setAllTitles('detail', response.full_name);
                contact.full_name = response.full_name;
            }

            if (field === 'twitter' || field === 'linkedin') {
                // Update the social media links.
                HLResource.setSocialMediaFields(response);

                contact.twitter = response.twitter;
                contact.linkedin = response.linkedin;
            }
        });

        return patchPromise;
    }

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

    return _contact;
}

