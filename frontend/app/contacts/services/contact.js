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

                    jsonData.active_at_account = checkActiveAt(jsonData);

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
                    let jsonData = angular.fromJson(data);
                    let objects = [];
                    let total = 0;

                    if (jsonData) {
                        if (jsonData.hits && jsonData.hits.length > 0) {
                            jsonData.hits.forEach(function(obj) {
                                obj.primary_email_address = $filter('primaryEmail')(obj.email_addresses);

                                objects.push(obj);
                            });
                        }

                        total = jsonData.total;
                    }

                    return {
                        objects: objects,
                        total: total,
                    };
                },
            },
            toggleActiveAtAccount: {
                method: 'PATCH',
                url: '/api/contacts/toggle_activation/',
            },
            getCalls: {
                url: '/api/contacts/:id/calls',
                transformResponse: data => {
                    let jsonData = angular.fromJson(data);

                    if (jsonData) {
                        if (jsonData.results && jsonData.results.length > 0) {
                            jsonData.results.map(call => {
                                call.activityType = 'call';
                                call.color = 'yellow';
                                call.date = call.start;
                            });
                        }
                    }

                    return jsonData;
                },
            },
        }
    );

    _contact.create = create;
    _contact.updateModel = updateModel;
    _contact.getSalutationOptions = getSalutationOptions;
    _contact.getGenderOptions = getGenderOptions;
    _contact.checkActiveAt = checkActiveAt;

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
            const oldAccounts = contact.accounts.map(team => ({'id': team.id}));
            const accountIds = args.accounts.map(team => team.id);
            let removedAccounts = oldAccounts.filter(team => accountIds.indexOf(team.id) === -1);
            for (let team of removedAccounts) team.is_deleted = true;
            args.accounts = args.accounts.map(team => ({'id': team.id})).concat(removedAccounts);
        }

        patchPromise = HLResource.patch('Contact', args).$promise;

        patchPromise.then(response => {
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

            if (args.hasOwnProperty('accounts')) {
                contact.active_at_account = checkActiveAt(response);
            }
        });

        return patchPromise;
    }

    function checkActiveAt(data) {
        let activeAtAccount = [];

        data.functions.forEach(func => {
            let accountId = func.account;

            data.accounts.forEach(account => {
                if (accountId === account.id) {
                    activeAtAccount[accountId] = func.is_active;
                }
            });
        });

        return activeAtAccount;
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

