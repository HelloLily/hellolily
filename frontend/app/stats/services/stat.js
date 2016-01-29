angular.module('app.stats.services').factory('Stats', Stats);

Stats.$inject = ['$resource'];
function Stats($resource) {
    var _stats = $resource(
        '/stats/:appname/:endpoint/:groupid',
        {}
    );

    return _stats;
}
