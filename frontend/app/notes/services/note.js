angular.module('app.notes').factory('Note', Note);

Note.$inject = ['$resource'];
function Note ($resource) {
    var Note = $resource('/api/notes/:id/',
        null,
        {
            update: {
                method: 'PATCH',
                params: {
                    id: '@id'
                }
            }
        }
    );

    /////

    return Note;
}
