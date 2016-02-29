angular.module('app.deals.services').factory('Deal', Deal);

Deal.$inject = ['$resource', 'HLUtils', 'HLForms', 'User'];
function Deal($resource, HLUtils, HLForms, User) {
    var _deal = $resource(
        '/api/deals/deal/:id/',
        null,
        {
            get: {
                transformResponse: function(data) {
                    var deal = angular.fromJson(data);

                    if (deal.contact) {
                        // API returns 'full_name' but ES returns 'name'. So get the full name and set the name.
                        deal.contact.name = deal.contact.full_name;
                    }

                    if (deal.assigned_to) {
                        deal.assigned_to.name = deal.assigned_to.full_name;
                    }

                    return deal;
                },
            },
            update: {
                method: 'PUT',
                params: {
                    id: '@id',
                },
                transformRequest: function(data) {
                    data = angular.copy(data);
                    return angular.toJson(HLForms.clean(data));
                },
            },
            save: {
                method: 'POST',
                transformRequest: function(data) {
                    data = angular.copy(data);
                    return angular.toJson(HLForms.clean(data));
                },
            },
            patch: {
                method: 'PATCH',
                params: {
                    id: '@id',
                },
                transformRequest: function(data) {
                    data = angular.copy(data);
                    return angular.toJson(HLForms.clean(data));
                },
            },
            query: {
                url: '/search/search/',
                method: 'GET',
                params: {
                    type: 'deals_deal',
                },
                isArray: true,
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);
                    var objects = [];

                    if (jsonData && jsonData.hits && jsonData.hits.length > 0) {
                        jsonData.hits.forEach(function(obj) {
                            var deal = $.extend(obj, {
                                historyType: 'deal',
                                color: 'blue',
                                date: obj.modified,
                                total_size: jsonData.total,
                            });

                            objects.push(deal);
                        });
                    }

                    return objects;
                },
            },
            getNextSteps: {
                url: 'api/deals/next-steps',
            },
            getWhyCustomer: {
                url: 'api/deals/why-customer',
            },
            getStages: {
                url: '/api/deals/stages',
                isArray: true,
                transformResponse: _transformChoices,
            },
            getFoundThrough: {
                url: '/api/deals/found-through',
                isArray: true,
                transformResponse: _transformChoices,
            },
            getContactedBy: {
                url: '/api/deals/contacted-by',
                isArray: true,
                transformResponse: _transformChoices,
            },
            getFormOptions: {
                url: 'api/deals/deal',
                method: 'OPTIONS',
            },
        }
    );

    _deal.getDeals = getDeals;
    _deal.create = create;
    _deal.prototype.markDealAsChecked = markDealAsChecked;
    _deal.prototype.feedbackFormSent = feedbackFormSent;

    /////////

    function create() {
        return new _deal({
            new_business: false,
            twitter_checked: false,
            is_checked: false,
            card_sent: false,
            feedback_form_sent: false,
            tags: [],
            currency: 'EUR',
            amount_once: 0,
            amount_recurring: 0,
            assigned_to: currentUser.id,
        });
    }

    /**
     * getDeals() gets the deals from the search backend through a promise
     *
     * @param queryString {string}: current search query on the deallist
     * @param page {int}: current page of pagination
     * @param pageSize {int}: current page size of pagination
     * @param orderColumn {string}: current sorting of deals
     * @param orderedDesc {boolean}: current ordering
     * @param filterQuery {string}: contains the filters which are used in ElasticSearch
     *
     * @returns Promise object: when promise is completed:
     *      {
     *          deals {list}: paginated deals objects
     *          total {int}: total number of deal objects
     *      }
     */
    function getDeals(queryString, page, pageSize, orderColumn, orderedDesc, filterQuery) {
        // Temporary fix to ensure the app doesn't break because of a non-existent column.
        if (orderColumn === 'closing_date') {
            orderColumn = 'next_step_date';
        }

        var sort = HLUtils.getSorting(orderColumn, orderedDesc);

        return _deal.query({
            q: queryString,
            page: page - 1,
            size: pageSize,
            sort: sort,
            filterquery: filterQuery,
        }, function(deals) {
            if (deals.length) {
                return {
                    deals: deals,
                    total: deals[0].total_size,
                };
            }
        }).$promise;
    }

    function feedbackFormSent() {
        var deal = this;
        deal.feedback_form_sent = true;
        return deal.$update();
    }

    function markDealAsChecked() {
        var deal = this;
        deal.is_checked = true;
        return deal.$update();
    }

    function _transformChoices(data) {
        data = angular.fromJson(data);
        var choices = [];

        // Convert the Django choices to a generic Array.
        for (var i = 0; i < data.length; i++) {
            choices.push({
                id: data[i][0],
                name: data[i][1],
            });
        }

        return choices;
    }

    return _deal;
}
