angular.module('app.accounts.services').factory('Account', Account);

Account.$inject = ['$http', '$q', '$resource'];
function Account($http, $q, $resource) {
    var Account = $resource(
        '/api/accounts/account/:id',
        null,
        {
            update: {
                method: 'PATCH',
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

    Account.getAccounts = getAccounts;
    Account.create = create;

    Account.prototype.getEmailAddress = getEmailAddress;
    Account.prototype.getDataproviderInfo = getDataproviderInfo;
    Account.prototype.addRelatedField = addRelatedField;
    Account.prototype.removeRelatedField = removeRelatedField;

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
    function getAccounts(queryString, page, pageSize, orderColumn, orderedAsc) {
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
            .then(function (response) {
                return {
                    accounts: response.data.hits,
                    total: response.data.total
                };
            });
    }

    function getEmailAddress() {
        var account = this;

        var primaryEmails = $filter('filter')(account.email_addresses, {status: 0});

        if (primaryEmails.length) {
            return primaryEmails[0];
        } else if (account.email_addresses.length) {
            return account.email_addresses[0];
        }
    }

    function create() {
        return new Account({
            name: '',
            primaryWebsite: '',
            email_addresses: [],
            phone_numbers: [],
            addresses: [],
            websites: [],
            tags: []
        });
    }

    function _sanitizeDomain(url) {
        var domain = $.trim(url.replace('http://', ''));
        domain = $.trim(domain.replace('https://', ''));
        // Always add last '/'
        if (domain.slice(-1) !== '/') {
            domain += '/';
        }
        return domain;
    }

    function getDataproviderInfo(url) {
        var account = this;
        var deferred = $q.defer();
        url = _sanitizeDomain(url);
        if (url.length > 1) {
            $http({
                url: '/provide/account/' + url
            }).success(function (response) {
                if (response.error) {
                    deferred.reject('Failed to load data');
                } else {
                    account._storeDataproviderInfo(response);
                    deferred.resolve();
                }
            }).error(function (error) {
                deferred.reject(error);
            });
        }

        return deferred.promise;
    }

    function addRelatedField(field) {
        var account = this;

        switch (field) {
            case 'emailAddress':
                // Default status is 'Other'
                var status = 1;
                var isPrimary = false;

                if (account.email_addresses.length == 0) {
                    // No email addresses added yet, so first one is primary
                    status = 2;
                    isPrimary = true;
                }

                account.email_addresses.push({is_primary: isPrimary, status: status});
                break;
            case 'phoneNumber':
                account.phone_numbers.push({type: 'work'});
                break;
            case 'address':
                account.addresses.push({type: 'visiting'});
                break;
            case 'website':
                account.websites.push({website: '', is_primary: false});
                break;
            default:
                break;
        }
    }

    function removeRelatedField(field, index, remove) {
        var account = this;

        switch (field) {
            case 'emailAddress':
                account.email_addresses[index].is_deleted = remove;
                break;
            case 'phoneNumber':
                account.phone_numbers[index].is_deleted = remove;
                break;
            case 'address':
                account.addresses[index].is_deleted = remove;
                break;
            case 'website':
                index = account.websites.indexOf(index);
                if (index != -1) {
                    account.websites[index].is_deleted = remove;
                }
                break;
            default:
                break;
        }
    }

    Account.prototype._storeDataproviderInfo = function (data) {
        var account = this;
        angular.forEach(data, function (value, key) {

            // Only if value is defined & is not an array (than it is an related field)
            if (value && !(value instanceof Array)) {
                account[key] = value;
            }
        });

        // Add related fields
        account._addEmailAddresses(data);
        account._addPhoneNumbers(data);
        account._addAddresses(data);
    };

    Account.prototype._addEmailAddresses = function (data) {
        var account = this;
        var newEmailAddresses = data.email_addresses;
        var primaryExists = false;

        if (data.primary_email) {
            primaryExists = true;
            newEmailAddresses.unshift(data.primary_email);
        }

        for (var i in newEmailAddresses) {
            var isPrimary = primaryExists && i == 0;
            var add = true;
            for (var j in account.email_addresses) {
                if (account.email_addresses[j].email_address == newEmailAddresses[i]) {
                    add = false;
                    break;
                }
            }

            if (add) {
                account.email_addresses.push({email_address: newEmailAddresses[i], is_primary: isPrimary});
            }
        }
    };

    Account.prototype._addPhoneNumbers = function (data) {
        var account = this;
        var newPhoneNumbers = data.phone_numbers;

        if (data.phone_number) {
            newPhoneNumbers.unshift(data.phone_number);
        }
        
        for (var i in newPhoneNumbers) {
            var add = true;
            for (var j in account.phone_numbers) {
                if (account.phone_numbers[j].raw_input == newPhoneNumbers[i]) {
                    add = false;
                    break;
                }
            }
            if (add) {
                account.phone_numbers.push({raw_input: newPhoneNumbers[i]});
            }
        }
    };

    Account.prototype._addAddresses = function (data) {
        var account = this;
        for (var i in data.addresses) {
            var add = true;
            for (var j in account.addresses) {
                add = false;
                for (var k in data.addresses[i]) {
                    if (data.addresses[i].hasOwnProperty(k)) {
                        if (account.addresses[j][k] != data.addresses[i][k]) {
                            add = true;
                        }
                    }
                }
                if (add) break;
            }
            if (add) {
                if (!data.addresses[i].type) {
                    data.addresses[i].type = 'visiting';
                }
                account.addresses.push(data.addresses[i]);
            }
        }
    };

    return Account;
}
