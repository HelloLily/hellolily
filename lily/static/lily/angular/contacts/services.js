/**
 * contactServices is a container for all contact related Angular services
 */
angular.module('contactServices', [])

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
