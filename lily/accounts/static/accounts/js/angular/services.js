/**
 * accountServices is a container for all account related Angular services
 */
var AccountServices = angular.module('AccountServices', [
    'ngResource'
]);

/**
 * $resource for Account model, now only used for detail page.
 */
AccountServices.factory('AccountDetail', ['$resource', function($resource) {
    function getPhone(account) {
        if (account.phone_mobile) return account.phone_mobile[0];
        if (account.phone_work) return account.phone_work[0];
        if (account.phone_other) return account.phone_other[0];
        return '';
    }
    function getPhones(account) {
        var phones = [];
        if (account.phone_mobile) phones = phones.concat(account.phone_mobile);
        if (account.phone_work) phones = phones.concat(account.phone_work);
        if (account.phone_other) phones = phones.concat(account.phone_other);
        return phones;
    }
    return $resource(
        '/search/search/?type=accounts_account&filterquery=id\::id',
        {},
        {
            get: {
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    if (data && data.hits && data.hits.length > 0) {
                        var account = data.hits[0];
                        account.phone = getPhone(account);
                        account.phones = getPhones(account);
                        return account;
                    }
                    return null;
                }
            },
            delete: {
                url: '/api/accounts/account/:id/',
                method: 'DELETE'
            }
        }
    );
}]);

/**
 * Account Service makes it possible to get Accounts from search backend
 *
 * @returns: Account object: object with functions related to Accounts
 */
AccountServices.factory('Account', ['$http', function($http) {
    var Account = {};

    /**
     * getAccounts() gets the accounts from the search backend trough a promise
     *
     * @param queryString string: current filter on the accountlist
     * @param page int: current page of pagination
     * @param pageSize int: current page size of pagination
     * @param orderColumn string: current sorting of accounts
     * @param orderedAsc {boolean}: current ordering
     *
     * @returns Promise object: when promise is completed:
     *      {
     *          accounts list: paginated account objects
     *          total int: total number of account objects
     *      }
     */
    var getAccounts = function(queryString, page, pageSize, orderColumn, orderedAsc) {

        var sort = '';
        if (orderedAsc) sort += '-';
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
        return getAccounts(table.filter, table.page, table.pageSize, table.order.column, table.order.ascending);
    };

    return Account;
}]);
