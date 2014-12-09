/**
 * accountServices is a container for all account related Angular services
 */
angular.module('accountServices', [])

    /**
     * Account Service makes it possible to get Accounts from search backend
     *
     * @returns: Account object: object with functions related to Accounts
     */
    .factory('Account', ['$http', function($http) {
        var Account = {};

        /**
         * getAccounts() gets the accounts from the search backend trough a promise
         *
         * @param queryString string: current filter on the accountlist
         * @param page int: current page of pagination
         * @param pageSize int: current page size of pagination
         * @param orderColumn string: current sorting of accounts
         * @param orderDirection {int|boolean|string}: current ordering of sorting
         *      if truthy ordering will be descending, otherwise ascending
         *
         * @returns Promise object: when promise is completed:
         *      {
         *          accounts list: paginated account objects
         *          total int: total number of account objects
         *      }
         */
        var getAccounts = function(queryString, page, pageSize, orderColumn, orderDirection) {

            var sort = '';
            if (orderDirection) sort += '-';
            sort += orderColumn;

            return $http({
                url: '/search/search/',
                method: 'GET',
                params: {
                    type: 'accounts_account',
                    q: queryString,
                    page: page - 1,
                    size: pageSize,
                    sort: sort
                }
            })
                .then(function(response) {
                    return {
                        accounts: response.data.hits,
                        total: response.data.total
                    };
                });
        };

        /**
         * query() makes it possible to query on accounts on backend search
         *
         * @param table object: holds all the info needed to get accounts from backend
         *
         * @returns Promise object: when promise is completed:
         *      {
         *          accounts list: paginated account objects
         *          total int: total number of account objects
         *      }
         */
        Account.query = function(table) {
            return getAccounts(table.filter, table.page, table.pageSize, table.order.column, table.order.direction);
        };

        return Account;
    }]);
