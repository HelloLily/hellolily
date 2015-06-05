angular.module('app.notes').factory('Note', Note);

Note.$inject = ['$resource'];
function Note ($resource) {
    return $resource('/api/notes/:id/');
}
