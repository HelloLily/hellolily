angular.module('app.accounts.services').factory('Account', Account);

Account.$inject = ['$http', '$q', '$resource', 'HLUtils'];
function Account($http, $q, $resource, HLUtils) {
    var Account = $resource(
        '/api/accounts/account/:id/',
        null,
        {
            search: {
                url: '/search/search/?type=accounts_account&filterquery=:filterquery',
                isArray: true,
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    var objects = [];
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function(obj) {
                            objects.push(obj);
                        });
                    }
                    return objects;
                },
            },
            update: {
                method: 'PUT',
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
            searchByEmail: {
                url: '/search/emailaddress/:email_address',
            },
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
     * @param queryString {string}: current filter on the accountlist
     * @param page {int}: current page of pagination
     * @param pageSize {int}: current page size of pagination
     * @param orderColumn {string}: current sorting of accounts
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
                sort: sort,
            },
        })
            .then(function(response) {
                return {
                    accounts: response.data.hits,
                    total: response.data.total,
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
            tags: [],
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
                url: '/provide/account/' + url,
            }).success(function(response) {
                if (response.error) {
                    deferred.reject('Failed to load data');
                } else {
                    account._storeDataproviderInfo(response);
                    deferred.resolve();
                }
            }).error(function(error) {
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

                if (account.email_addresses.length === 0) {
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
                if (index !== -1) {
                    account.websites[index].is_deleted = remove;
                }
                break;
            default:
                break;
        }
    }

    Account.prototype._storeDataproviderInfo = function(data) {
        var account = this;
        angular.forEach(data, function(value, key) {
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

    Account.prototype._addEmailAddresses = function(data) {
        var account = this;

        angular.forEach(data.email_addresses, function(emailAddress) {
            var add = true;

            angular.forEach(account.email_addresses, function(accountEmailAddress) {
                // Check if email address already exists
                if (emailAddress === accountEmailAddress.email_address) {
                    add = false;
                }
            });

            if (add) {
                if (data.primary_email && data.primary_email === emailAddress) {
                    account.email_addresses.unshift({email_address: emailAddress, is_primary: true, status: 2});
                } else {
                    account.email_addresses.push({email_address: emailAddress, is_primary: false, status: 1});
                }
            }
        });
    };

    Account.prototype._addPhoneNumbers = function(data) {
        var account = this;

        angular.forEach(data.phone_numbers, function(phoneNumber) {
            var add = true;

            angular.forEach(account.phone_numbers, function(accountPhoneNumber) {
                // Check if phone number already exists
                if (phoneNumber === accountPhoneNumber.raw_input) {
                    add = false;
                }
            });

            if (add) {
                phoneNumber = HLUtils.formatPhoneNumber({raw_input: phoneNumber, type: 'work'});

                account.phone_numbers.push(phoneNumber);
            }
        });
    };

    Account.prototype._addAddresses = function(data) {
        var account = this;

        angular.forEach(data.addresses, function(address) {
            if (!address.type) {
                address.type = 'visiting';
            }

            var add = true;

            angular.forEach(account.addresses, function(accountAddress) {
                // Check if address already exists
                if (angular.equals(address, accountAddress)) {
                    add = false;
                }
            });

            if (add) {
                account.addresses.push(address);
            }
        });
    };

    return Account;
}
