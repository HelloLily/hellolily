/**
 * HLCache Service provides a way to re-use one cache for different APIs.
 */

angular.module('app.services').service('HLCache', HLCache);

HLCache.$inject = ['CacheFactory'];
function HLCache(CacheFactory) {
    // Create the cache.
    new CacheFactory('dataCache', {
        // Items added to this cache expire after 5 minutes.
        maxAge: 5 * 60 * 1000,
        // Expired items will remain in the cache until requested, at which point they are removed.
        deleteOnExpire: 'passive',
    });

    new CacheFactory('userCache', {
        // Items added to this cache expire after 5 minutes.
        maxAge: 5 * 60 * 1000,
        // Expired items will remain in the cache until requested, at which point they are removed.
        deleteOnExpire: 'passive',
    });

    new CacheFactory('volatileCache', {
        // Items added to this cache expire after 5 seconds.
        maxAge: 5 * 1000,
        // Expired items will remain in the cache until requested, at which point they are removed.
        deleteOnExpire: 'passive',
    });
}
