angular.module('app.cases.services').factory('CaseStatuses', CaseStatuses);

CaseStatuses.$inject = ['$resource', 'HLCache', 'CacheFactory'];
function CaseStatuses($resource, HLCache, CacheFactory) {
    return $resource(
        '/api/cases/statuses',
        {},
        {
            query: {
                isArray: true,
                cache: CacheFactory.get('dataCache'),
            },
        }
    );
}
