angular.module('app.accounts.services').factory('Account', Account);

Account.$inject = ['$filter', '$http', '$q', '$resource', 'HLResource', 'HLUtils', 'HLCache',
    'CacheFactory', 'Settings'];
function Account($filter, $http, $q, $resource, HLResource, HLUtils, HLCache,
    CacheFactory, Settings) {
    var _account = $resource(
        '/api/accounts/:id/',
        null,
        {
            get: {
                // TODO: LILY-1659: Apply caching on User Account.
                //cache: CacheFactory.get('dataCache'),
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);

                    HLResource.setSocialMediaFields(jsonData);

                    jsonData.primary_email_address = $filter('primaryEmail')(jsonData.email_addresses);

                    return jsonData;
                },
            },
            query: {
                // TODO: LILY-1659: Apply caching on User Account.
                //cache: CacheFactory.get('dataCache'),
                isArray: false,
            },
            search: {
                url: '/api/accounts/',
                cache: true,
                transformResponse: function(data) {
                    let jsonData = angular.fromJson(data);
                    let objects = [];
                    let total = 0;

                    if (jsonData) {
                        if (jsonData.hits && jsonData.hits.length > 0) {
                            jsonData.hits.forEach(function(obj) {
                                objects.push(obj);
                            });
                        }

                        total = jsonData.total;
                    }

                    return {
                        objects: objects,
                        total: total,
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
            searchByPhoneNumber: {
                url: '/search/number/:number',
            },
            getCalls: {
                url: '/api/accounts/:id/calls',
                transformResponse: data => {
                    let jsonData = angular.fromJson(data);

                    if (jsonData) {
                        if (jsonData.results && jsonData.results.length > 0) {
                            jsonData.results.map(call => {
                                call.activityType = 'call';
                                call.color = 'yellow';
                                call.date = call.start;
                            });
                        }
                    }

                    return jsonData;
                },
            },
        });

    _account.getAccounts = getAccounts;
    _account.create = create;
    _account.updateModel = updateModel;

    _account.prototype.getDataproviderInfo = getDataproviderInfo;

    // Make sure account statuses are available without an extra call to statuses.
    _account.getStatuses();

    //////

    /**
     * getAccounts() gets the accounts from the search backend through a promise
     *
     * @param queryString {string}: current filter on the accountlist
     * @param page {int}: current page of pagination
     * @param pageSize {int}: current page size of pagination
     * @param orderColumn {string}: current sorting of accounts
     * @param orderedAsc {boolean}: current ordering
     * @param filterQuery {string}: Contains the filters which are used in Elasticsearch.
     *
     * @returns Promise object: when promise is completed:
     *      {
     *          accounts list: paginated account objects
     *          total int: total number of account objects
     *      }
     */
    function getAccounts(queryString, page, pageSize, orderColumn, orderedAsc, filterQuery) {
        var sort = '';
        if (orderedAsc) sort += '-';
        sort += orderColumn;

        return $http({
            url: '/api/accounts/',
            method: 'GET',
            params: {
                search: queryString,
                page: page,
                page_size: pageSize,
                ordering: sort,
            },
        }).then(function(response) {
            return {
                accounts: response.data.results,
                total: response.data.pagination.total,
            };
        });
    }

    function updateModel(data, field, account) {
        var patchPromise;
        var args = HLResource.createArgs(data, field, account);

        if (field === 'twitter') {
            args = {
                id: account.id,
                social_media: [args],
            };
        }

        if (field === 'name') {
            Settings.page.setAllTitles('detail', data);
        }

        patchPromise = HLResource.patch('Account', args).$promise;

        patchPromise.then(function(response) {
            if (field === 'twitter') {
                // Update the Twitter link.
                HLResource.setSocialMediaFields(response);

                account.twitter = response.twitter;
            }

            if (field === 'customer_id') {
                // Change status to Active if customer_id is succesfully updated.
                _account.getStatuses(function(statusResponse) {
                    args = {
                        id: account.id,
                        status: _account.relationStatus.id,
                    };
                    if (account.status.id === _account.relationStatus.id) {
                        HLResource.patch('Account', args).$promise;
                        account.status = _account.activeStatus;
                    }
                });
            }
        });

        return patchPromise;
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
                url: '/api/provide/dataprovider/',
                method: 'POST',
                data: {url: sanitizedUrl},
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
        account._addAddresses(data);
        account._addPhoneNumbers(data);
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

    _account.prototype._addPhoneNumbers = function(data) {
        var account = this;
        var formattedPhoneNumber;
        var address;

        angular.forEach(data.phone_numbers, function(phoneNumber) {
            var add = true;

            angular.forEach(account.phone_numbers, function(accountPhoneNumber) {
                // Check if phone number already exists
                if (phoneNumber === accountPhoneNumber.number) {
                    add = false;
                }
            });

            if (add) {
                if (account.addresses.length) {
                    address = account.addresses[0];
                }

                formattedPhoneNumber = HLUtils.formatPhoneNumber({number: phoneNumber, type: 'work'}, address);

                account.phone_numbers.push(formattedPhoneNumber);
            }
        });
    };

    return _account;
}
