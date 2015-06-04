/**
 * $resource for Case model, now only used for detail page.
 */
angular.module('app.cases.services').factory('CaseDetail', CaseDetail);

CaseDetail.$inject = ['$resource'];
function CaseDetail ($resource) {
    return $resource(
        '/search/search/?type=cases_case&filterquery=id\::id',
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
                url: '/search/search/?type=cases_case&filterquery=:filterquery',
                isArray: true,
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    var objects = [];
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function(obj) {
                            obj = $.extend(obj, {historyType: 'case', color: 'grey', date: obj.expires});
                            objects.push(obj);
                        });
                    }
                    return objects;
                }
            },
            totalize: {
                url: '/search/search/?type=cases_case&size=0&filterquery=:filterquery',
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
