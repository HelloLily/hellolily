angular.module('app.services').factory('AppHash', AppHash);

AppHash.$inject = ['$resource', 'HLCache', 'CacheFactory'];
function AppHash($resource, HLCache, CacheFactory) {
    return $resource(
        '/api/utils/apphash/',
        null,
        {
            get: {
                cache: CacheFactory.get('dataCache'),
            },
        }
    );
}
