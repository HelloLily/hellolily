angular.module('app.deals.services').factory('DealDetail', DealDetail);

DealDetail.$inject = ['$resource'];
function DealDetail($resource) {
    var _dealDetail = $resource(
        '/search/search/?type=deals_deal&filterquery=id\::id',
        {},
        {
            get: {
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);
                    if (jsonData && jsonData.hits && jsonData.hits.length > 0) {
                        return jsonData.hits[0];
                    }
                    return null;
                },
            },
            query: {
                url: '/search/search/?type=deals_deal&filterquery=:filterquery',
                isArray: true,
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);
                    var objects = [];

                    if (jsonData && jsonData.hits && jsonData.hits.length > 0) {
                        jsonData.hits.forEach(function(obj) {
                            var deal = $.extend(obj, {historyType: 'deal', color: 'blue', date: obj.modified});
                            objects.push(deal);
                        });
                    }

                    return objects;
                },
            },
            totalize: {
                url: '/search/search/?type=deals_deal&size=0&filterquery=:filterquery',
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);

                    if (jsonData && jsonData.total) {
                        return {total: jsonData.total};
                    }

                    return {total: 0};
                },
            },
        }
    );

    return _dealDetail;
}
