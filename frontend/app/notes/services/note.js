angular.module('app.notes').factory('Note', Note);

Note.$inject = ['$resource', 'HLResource'];
function Note($resource, HLResource) {
    var _note = $resource(
        '/api/notes/:id/',
        null,
        {
            query: {
                isArray: false,
            },
            update: {
                method: 'PATCH',
                params: {
                    id: '@id',
                },
            },
            patch: {
                method: 'PATCH',
                params: {
                    id: '@id',
                },
            },
        }
    );

    _note.updateModel = updateModel;

    /////////

    function updateModel(data, field, noteObject) {
        var patchPromise;
        var args = HLResource.createArgs(data, field, noteObject);

        if (field === 'name') {
            Settings.page.setAllTitles('detail', data);
        }

        patchPromise = HLResource.patch('Note', args).$promise;

        return patchPromise;
    }

    return _note;
}
