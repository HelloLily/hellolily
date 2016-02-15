angular.module('app.contacts.services').factory('ContactDetail', ContactDetail);

ContactDetail.$inject = ['$resource', 'HLObjectDetails'];
function ContactDetail($resource, HLObjectDetails) {
    var _contactDetail = $resource(
        '/search/search/?type=contacts_contact&filterquery=id\::id',
        {},
        {
            get: {
                transformResponse: function (data) {
                    data = angular.fromJson(data);
                    if (data && data.hits && data.hits.length > 0) {
                        var contact = data.hits[0];
                        contact.phones = HLObjectDetails.getPhones(contact);
                        contact.phone = HLObjectDetails.getPhone(contact);
                        contact.email_addresses = HLObjectDetails.getEmailAddresses(contact);

                        return contact;
                    }

                    return null;
                }
            },
            query: {
                url: '/search/search/?type=contacts_contact&size=1000&filterquery=:filterquery&sort=full_name',
                isArray: true,
                transformResponse: function (data) {
                    data = angular.fromJson(data);
                    var contacts = [];
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function (contact) {
                            contact.phones = HLObjectDetails.getPhones(contact);
                            contact.phone = HLObjectDetails.getPhone(contact);
                            contact.email_addresses = HLObjectDetails.getEmailAddresses(contact);
                            contacts.push(contact);
                        });
                    }

                    return contacts;
                }
            }
        }
    )

    return _contactDetail;
}
