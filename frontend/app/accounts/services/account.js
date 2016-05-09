angular.module('app.accounts.services').factory('Account', Account);

Account.$inject = ['$http', '$q', '$resource', 'HLResource', 'HLUtils', 'HLCache', 'CacheFactory'];
function Account($http, $q, $resource, HLResource, HLUtils, HLCache, CacheFactory) {
    var _account = $resource(
        '/api/accounts/account/:id/',
        null,
        {
            get: {
                // TODO: LILY-1659: Apply caching on User Account.
                //cache: CacheFactory.get('dataCache'),
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);

                    HLResource.setSocialMediaFields(jsonData);

                    return jsonData;
                },
            },
            query: {
                // TODO: LILY-1659: Apply caching on User Account.
                //cache: CacheFactory.get('dataCache'),
                isArray: false,
            },
            search: {
                url: '/search/search/?type=accounts_account&filterquery=:filterquery',
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);
                    var objects = [];

                    if (jsonData && jsonData.hits && jsonData.hits.length > 0) {
                        jsonData.hits.forEach(function(obj) {
                            objects.push(obj);
                        });
                    }

                    return {
                        objects: objects,
                        total: jsonData.total,
                    };
                },
            },
            update: {
                method: 'PUT',
                params: {
                    id: '@id',
                },
            },
            patch: {
                method: 'PATCH',
                params: {
                    id: '@id',
                },
            },
            delete: {
                method: 'DELETE',
            },
            addressOptions: {
                cache: CacheFactory.get('dataCache'),
                url: '/api/utils/countries/',
                method: 'OPTIONS',
            },
            searchByEmail: {
                url: '/search/emailaddress/:email_address',
            },
            getStatuses: {
                url: '/api/accounts/statuses/',
                transformResponse: function(data) {
                    var statusData = angular.fromJson(data);

                    angular.forEach(statusData.results, function(status) {
                        if (status.name === 'Relation') {
                            _account.relationStatus = status;
                            _account.defaultNewStatus = _account.relationStatus;
                        } else if (status.name === 'Active') {
                            _account.activeStatus = status;
                        }
                    });

                    return statusData;
                },
            },
            searchByWebsite: {
                url: '/search/website/:website',
            },
        });

    _account.getAccounts = getAccounts;
    _account.create = create;

    _account.prototype.getEmailAddress = getEmailAddress;
    _account.prototype.getDataproviderInfo = getDataproviderInfo;
    _account.prototype.addRelatedField = addRelatedField;
    _account.prototype.removeRelatedField = removeRelatedField;

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
        return new _account({
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
        var sanitizedUrl = _sanitizeDomain(url);

        if (sanitizedUrl.length > 1) {
            $http({
                url: '/provide/account/' + sanitizedUrl,
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

    _account.prototype._storeDataproviderInfo = function(data) {
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

    _account.prototype._addEmailAddresses = function(data) {
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

    _account.prototype._addPhoneNumbers = function(data) {
        var account = this;
        var formattedPhoneNumber;

        angular.forEach(data.phone_numbers, function(phoneNumber) {
            var add = true;

            angular.forEach(account.phone_numbers, function(accountPhoneNumber) {
                // Check if phone number already exists
                if (phoneNumber === accountPhoneNumber.number) {
                    add = false;
                }
            });

            if (add) {
                formattedPhoneNumber = HLUtils.formatPhoneNumber({number: phoneNumber, type: 'work'});

                account.phone_numbers.push(formattedPhoneNumber);
            }
        });
    };

    _account.prototype._addAddresses = function(data) {
        var account = this;
        var add = true;

        angular.forEach(data.addresses, function(address) {
            if (!address.type) {
                address.type = 'visiting';
            }

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

    return _account;
}
