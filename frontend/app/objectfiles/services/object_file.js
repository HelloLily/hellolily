angular.module('app.objectfiles.services').factory('ObjectFile', ObjectFile);

ObjectFile.$inject = ['$resource', 'HLResource'];
function ObjectFile($resource, HLResource) {
    const _objectFile = $resource(
        '/api/files/:id/',
        null,
        {
            patch: {
                method: 'PATCH',
                params: {
                    id: '@id',
                },
            },
            getForObject: {
                url: '/api/:model/:id/files/',
                params: {
                    id: '@id',
                    model: '@model',
                },
            },
            delete: {
                method: 'DELETE',
            },
        }
    );

    /////////

    return _objectFile;
}
