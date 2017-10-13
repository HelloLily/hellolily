angular.module('app.calls').factory('Call', Call);

Call.$inject = ['$resource'];
function Call($resource) {
    var _call = $resource(
        '/api/call-records/:id/',
        null,
        {
            getLatestCall: {
                url: '/api/call-records/latest/',
            },
        });

    return _call;
}
