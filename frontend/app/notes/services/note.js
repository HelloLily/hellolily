angular.module('app.notes').factory('Note', Note);

Note.$inject = ['$resource', 'HLResource'];
function Note($resource, HLResource) {
    const _note = $resource(
        '/api/notes/:id/',
        null,
        {
            search: {
                url: '/search/search/?type=notes_note&size=:size&sort=-date&filterquery=:filterquery',
                isArray: true,
                transformResponse: data => {
                    const jsonData = angular.fromJson(data);
                    const objects = [];

                    if (jsonData && jsonData.hits && jsonData.hits.length > 0) {
                        jsonData.hits.forEach(obj => {
                            const noteObject = $.extend(obj, {activityType: 'note', color: 'yellow'});
                            objects.push(noteObject);
                        });
                    }

                    return objects;
                },
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
            delete: {
                method: 'DELETE',
            },
        }
    );

    _note.updateModel = updateModel;

    /////////

    function updateModel(data, field, noteObject) {
        const args = HLResource.createArgs(data, field, noteObject);

        if (field === 'name') {
            Settings.page.setAllTitles('detail', data);
        }

        const patchPromise = HLResource.patch('Note', args).$promise;

        return patchPromise;
    }

    return _note;
}
