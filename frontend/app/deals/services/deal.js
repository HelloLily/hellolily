angular.module('app.deals.services').factory('Deal', Deal);

Deal.$inject = ['$resource', 'HLUtils'];
function Deal($resource, HLUtils) {
    var _deal = $resource(
        '/api/deals/deal/:id',
        null,
        {
            update: {
                method: 'PATCH',
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
            nextSteps: {
                isArray: true,
                url: 'api/deals/nextsteps',
            },
        }
    );

    _deal.getDeals = getDeals;
    _deal.prototype.markDealAsChecked = markDealAsChecked;
    _deal.prototype.feedbackFormSent = feedbackFormSent;

    /////

    /**
     * getDeals() gets the deals from the search backend through a promise
     *
     * @param queryString string: current search query on the deallist
     * @param page int: current page of pagination
     * @param pageSize int: current page size of pagination
     * @param orderColumn string: current sorting of deals
     * @param orderedDesc {boolean}: current ordering
     * @param filterQuery {string}: contains the filters which are used in ElasticSearch
     *
     * @returns Promise object: when promise is completed:
     *      {
     *          deals list: paginated deals objects
     *          total int: total number of deal objects
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

    return _deal;
}
