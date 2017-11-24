angular.module('app.accounts.services').factory('Account', Account);

Account.$inject = ['$filter', '$http', '$q', '$resource', 'HLResource', 'HLUtils', 'HLCache',
    'CacheFactory', 'Settings'];
function Account($filter, $http, $q, $resource, HLResource, HLUtils, HLCache,
    CacheFactory, Settings) {
    const _account = $resource(
        '/api/accounts/:id/',
        null,
        {
            get: {
                // TODO: LILY-1659: Apply caching on User Account.
                //cache: CacheFactory.get('dataCache'),
                transformResponse: data => {
                    const jsonData = angular.fromJson(data);

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
                url: '/search/search/?type=accounts_account&filterquery=:filterquery',
                cache: true,
                transformResponse: data => {
                    const jsonData = angular.fromJson(data);
                    const objects = [];
                    let total = 0;

                    if (jsonData) {
                        if (jsonData.hits && jsonData.hits.length > 0) {
                            jsonData.hits.forEach(obj => {
                                objects.push(obj);
                            });
                        }

                        total = jsonData.total;
                    }

                    return {
                        objects,
                        total,
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
                transformResponse: data => {
                    const statusData = angular.fromJson(data);

                    angular.forEach(statusData.results, status => {
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
            searchByPhoneNumber: {
                url: '/search/number/:number',
            },
            getCalls: {
                url: '/api/accounts/:id/calls',
                transformResponse: data => {
                    const jsonData = angular.fromJson(data);

                    if (jsonData) {
                        if (jsonData.results && jsonData.results.length > 0) {
                            jsonData.results.forEach(call => {
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
        let sort = '';
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
                filterquery: filterQuery,
            },
        }).then(response => {
            return {
                accounts: response.data.hits,
                total: response.data.total,
            };
        });
    }

    function updateModel(data, field, account) {
        let args = HLResource.createArgs(data, field, account);

        if (field === 'twitter') {
            args = {
                id: account.id,
                social_media: [args],
            };
        }

        if (field === 'name') {
            Settings.page.setAllTitles('detail', data);
        }

        const patchPromise = HLResource.patch('Account', args).$promise;

        patchPromise.then(response => {
            if (field === 'twitter') {
                // Update the Twitter link.
                HLResource.setSocialMediaFields(response);

                account.twitter = response.twitter;
            }

            if (field === 'customer_id') {
                // Change status to Active if customer_id is succesfully updated.
                _account.getStatuses(statusResponse => {
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
        let domain = $.trim(url.replace('http://', ''));
        domain = $.trim(domain.replace('https://', ''));

        // Always add last '/'
        if (domain.slice(-1) !== '/') {
            domain += '/';
        }

        return domain;
    }

    function getDataproviderInfo(url) {
        const account = this;
        const deferred = $q.defer();
        const sanitizedUrl = _sanitizeDomain(url);

        if (sanitizedUrl.length > 1) {
            $http({
                url: '/api/provide/dataprovider/',
                method: 'POST',
                data: {url: sanitizedUrl},
            }).success(response => {
                if (response.error) {
                    deferred.reject('Failed to load data');
                } else {
                    account._storeDataproviderInfo(response);
                    deferred.resolve();
                }
            }).error(error => {
                deferred.reject(error);
            });
        }

        return deferred.promise;
    }

    _account.prototype._storeDataproviderInfo = function(data) {
        const account = this;

        angular.forEach(data, (value, key) => {
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
        const account = this;

        angular.forEach(data.email_addresses, emailAddress => {
            let add = true;

            angular.forEach(account.email_addresses, (accountEmailAddress) => {
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
        const account = this;
        let add = true;

        angular.forEach(data.addresses, address => {
            if (!address.type) {
                address.type = 'visiting';
            }

            angular.forEach(account.addresses, accountAddress => {
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
        const account = this;

        angular.forEach(data.phone_numbers, phoneNumber => {
            let add = true;

            angular.forEach(account.phone_numbers, accountPhoneNumber => {
                // Check if phone number already exists
                if (phoneNumber === accountPhoneNumber.number) {
                    add = false;
                }
            });

            if (add) {
                let address;

                if (account.addresses.length) {
                    address = account.addresses[0];
                }

                const formattedPhoneNumber = HLUtils.formatPhoneNumber({number: phoneNumber, type: 'work'}, address);

                account.phone_numbers.push(formattedPhoneNumber);
            }
        });
    };

    return _account;
}
