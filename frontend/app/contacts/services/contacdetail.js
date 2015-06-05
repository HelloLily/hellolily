angular.module('app.contacts.services').factory('ContactDetail', ContactDetail);

ContactDetail.$inject = ['$resource'];
function ContactDetail ($resource) {
    function getPhone(contact) {
        if (contact.phone_mobile) return contact.phone_mobile[0];
        if (contact.phone_work) return contact.phone_work[0];
        if (contact.phone_other) return contact.phone_other[0];
        return '';
    }

    function getPhones(contact) {
        var phones = [];
        if (contact.phone_mobile) phones = phones.concat(contact.phone_mobile);
        if (contact.phone_work) phones = phones.concat(contact.phone_work);
        if (contact.phone_other) phones = phones.concat(contact.phone_other);
        return phones;
    }

    return $resource(
        '/search/search/?type=contacts_contact&filterquery=id\::id',
        {},
        {
            get: {
                transformResponse: function (data) {
                    data = angular.fromJson(data);
                    if (data && data.hits && data.hits.length > 0) {
                        var contact = data.hits[0];
                        contact.phones = getPhones(contact);
                        contact.phone = getPhone(contact);
                        return contact;
                    }
                    return null;
                }
            },
            query: {
                url: '/search/search/?type=contacts_contact&size=1000&filterquery=:filterquery',
                isArray: true,
                transformResponse: function (data) {
                    data = angular.fromJson(data);
                    var contacts = [];
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function (contact) {
                            contact.phones = getPhones(contact);
                            contact.phone = getPhone(contact);
                            contacts.push(contact);
                        });
                    }
                    return contacts;
                }
            }
        }
    )
}
