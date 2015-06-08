angular.module('app.accounts.services').factory('Account', Account);

Account.$inject = ['$filter', '$http', '$resource'];
function Account ($filter, $http, $resource) {
    var Account = $resource(
        '/api/accounts/account/:id',
        null,
        {
            update: {
                method: 'PUT',
                params: {
                    id: '@id'
                }
            },
            delete:  {
                method: 'DELETE'
            }
        });

    Account.getAccounts = getAccounts;
    Account.prototype.getEmailAddress = getEmailAddress;

    //////

    /**
     * getAccounts() gets the accounts from the search backend through a promise
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
    function getAccounts (queryString, page, pageSize, orderColumn, orderedAsc) {

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
    }

    function getEmailAddress() {
        var account = this;

        var primaryEmails = $filter('filter')(account.email_addresses, {status: 2});

        if (primaryEmails.length) {
            return primaryEmails[0];
        } else if (account.email_addresses.length) {
            return account.email_addresses[0];
        }
    }
    return Account;
}
