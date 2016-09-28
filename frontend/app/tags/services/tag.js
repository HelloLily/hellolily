angular.module('app.tags.services').factory('Tag', Tag);

Tag.$inject = ['$resource'];
function Tag($resource) {
    var _tag = $resource(
        '/api/tags/tag/:id',
        {},
        {
            search: {
                url: '/search/search/?type=tags_tag&facet_field=name_flat&facet_filter=name::query&size=60',
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);
                    var objects = [];

                    if (jsonData && jsonData.facets && jsonData.facets.length > 0) {
                        jsonData.facets.forEach(function(obj) {
                            var lastUsed = obj.last_used ? obj.last_used : '';

                            objects.push({
                                name: obj.term,
                                count: obj.count,
                                last_used: lastUsed,
                            });
                        });
                    }

                    return {
                        objects: objects,
                        total: jsonData.total,
                    };
                },
            },
        }
    );

    return _tag;
}
