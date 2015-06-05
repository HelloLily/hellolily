angular.module('app.deals.services').factory('DealDetail', DealDetail);

DealDetail.$inject = ['$resource'];
function DealDetail ($resource) {
    return $resource(
        '/search/search/?type=deals_deal&filterquery=id\::id',
        {},
        {
            get: {
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    if (data && data.hits && data.hits.length > 0) {
                        var obj = data.hits[0];
                        return obj;
                    }
                    return null;
                }
            },
            query: {
                url: '/search/search/?type=deals_deal&filterquery=:filterquery',
                isArray: true,
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    var objects = [];
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function(obj) {
                            obj = $.extend(obj, {historyType: 'deal', color: 'blue', date: obj.modified});
                            objects.push(obj)
                        });
                    }
                    return objects;
                }
            },
            totalize: {
                url: '/search/search/?type=deals_deal&size=0&filterquery=:filterquery',
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    if (data && data.total) {
                        return {total: data.total};
                    }
                    return {total: 0};
                }
            }
        }
    );
}
