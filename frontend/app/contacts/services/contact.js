angular.module('app.contacts.services').factory('Contact', Contact);

Contact.$inject = ['$http', '$resource'];
function Contact ($http, $resource) {
      var Contact = $resource(
        '/api/contacts/contact/:id/',
        null,
        {
            update: {
                method: 'PUT',
                params: {
                    id: '@id'
                }
            },
            delete: {
                method: 'DELETE'
            },
            addressOptions: {
                url: '/api/utils/countries/',
                method: 'OPTIONS'
            }
        });

    Contact.getContacts = getContacts;
    Contact.create = create;

    //////

    /**
     * getContacts() get the contacts from the search backend through a promise
     *
     * @param queryString {string}: current filter on the contactlist
     * @param page {int}: current page of pagination
     * @param pageSize {int}: current page size of pagination
     * @param orderColumn {string}: current sorting of contacts
     * @param orderedAsc {boolean}: current ordering
     *
     * @returns Promise object: when promise is completed:
     *      {
     *          contacts list: paginated contact objects
     *          total int: total number of contact objects
     *      }
     */
    function getContacts(queryString, page, pageSize, orderColumn, orderedAsc) {

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
    }

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
            accounts: []
        });
    }

    return Contact;
}

