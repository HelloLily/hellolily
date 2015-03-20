/**
 * noteServices is a container for all Note related Angular services
 */
angular.module('noteServices', ['ngResource'])

/**
 * $resource for Note model.
 */
    .factory('NoteDetail', ['$resource', function($resource) {
        return $resource(
            '/search/search/?type=notes_note&filterquery=id\::id',
            {size:100},
            {
                get: {
                    transformResponse: function(data) {
                        data = angular.fromJson(data);
                        if (data && data.hits && data.hits.length > 0) {
                            var obj = data.hits[0];
                            return obj;
                        }
                        return null;
                    }
                },
                query: {
                    url: '/search/search/?type=notes_note&size=:size&sort=-date&filterquery=:filterquery',
                    isArray: true,
                    transformResponse: function(data) {
                        data = angular.fromJson(data);
                        var objects = [];
                        if (data && data.hits && data.hits.length > 0) {
                            data.hits.forEach(function(obj) {
                                objects.push(obj)
                            });
                        }
                        return objects;
                    }
                },
                totalize: {
                    url: '/search/search/?type=notes_note&size=0&filterquery=:filterquery',
                    transformResponse: function(data) {
                        data = angular.fromJson(data);
                        if (data && data.total) {
                            return {total: data.total};
                        }
                        return {total: 0};
                    }
                }
            }
        );
    }]);
