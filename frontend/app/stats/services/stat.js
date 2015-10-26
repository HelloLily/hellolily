angular.module('app.stats.services').factory('Stats', Stats);

Stats.$inject = ['$resource'];
function Stats($resource) {
    var Stats = $resource(
        '/stats/:appname/:endpoint/:groupid',
        {}
    );

    return Stats;
}
