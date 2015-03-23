/**
 * contactServices is a container for all contact related Angular services
 */
angular.module('contactServices', ['ngResource'])

/**
 * $resource for Contact model, now only used for detail page.
 */
    .factory('ContactDetail', ['$resource', function($resource) {
        function getPhone(contact) {
            if (contact.phone_mobile) return contact.phone_mobile[0];
            if (contact.phone_work) return contact.phone_work[0];
            if (contact.phone_other) return contact.phone_other[0];
            return '';
        }
        function getPhones(contact) {
            var phones = [];
            if (contact.phone_mobile) phones = phones.concat(contact.phone_mobile)
            if (contact.phone_work) phones = phones.concat(contact.phone_work)
            if (contact.phone_other) phones = phones.concat(contact.phone_other)
            return phones;
        }
        return $resource(
            '/search/search/?type=contacts_contact&filterquery=id\::id',
            {},
            {
                get: {
                    transformResponse: function(data) {
                        data = angular.fromJson(data);
                        if (data && data.hits && data.hits.length > 0) {
                            var contact = data.hits[0];
                            contact.phones = getPhones(contact);
                            contact.phone = getPhone(contact);
                            console.log(contact);
                            return contact;
                        }
                        console.log('return null');
                        return null;
                    }
                },
                query: {
                    url: '/search/search/?type=contacts_contact&size=1000&filterquery=:filterquery',
                    isArray: true,
                    transformResponse: function(data) {
                        console.log('contact query');
                        data = angular.fromJson(data);
                        var contacts = [];
                        if (data && data.hits && data.hits.length > 0) {
                            data.hits.forEach(function(contact) {
                                contact.phones = getPhones(contact);
                                contact.phone = getPhone(contact);
                                contacts.push(contact);
                            });
                        }
                        return contacts;
                    }
                }
            }
        );
    }])

/**
 * Contact Service makes it possible to get Contacts from search backend
 *
 * @returns: Contact object: object with functions related to Contacts
 */
    .factory('Contact', ['$http', function($http) {
        var Contact = {};

        /**
         * getContacts() get the contacts from the search backend trough a promise
         *
         * @param queryString string: current filter on the contactlist
         * @param page int: current page of pagination
         * @param pageSize int: current page size of pagination
         * @param orderColumn string: current sorting of contacts
         * @param orderedAsc {boolean}: current ordering
         *
         * @returns Promise object: when promise is completed:
         *      {
         *          contacts list: paginated contact objects
         *          total int: total number of contact objects
         *      }
         */
        var getContacts = function(queryString, page, pageSize, orderColumn, orderedAsc) {

            var sort = '';
            if (orderedAsc) sort += '-';
            sort += orderColumn;

            return $http({
                url: '/search/search/',
                method: 'GET',
                params: {
                    type: 'contacts_contact',
                    q: queryString,
                    page: page - 1,
                    size: pageSize,
                    sort: sort
                }
            })
                .then(function(response) {
                    return {
                        contacts: response.data.hits,
                        total: response.data.total
                    };
                });
        };

        /**
         * query() makes it possible to query on contacts on backend search
         *
         * @param table object: holds all the info needed to get contacts from backend
         *
         * @returns Promise object: when promise is completed:
         *      {
         *          contacts list: paginated contact objects
         *          total int: total number of contact objects
         *      }
         */
        Contact.query = function(table) {
            return getContacts(table.filter, table.page, table.pageSize, table.order.column, table.order.ascending);
        };

        return Contact;
    }]);
