angular.module('app.tags.services').factory('Tag', Tag);

Tag.$inject = ['$resource'];
function Tag($resource) {
    var _tag = $resource(
        '/api/tags/tag/:id',
        {},
        {
            query: {
                url: '/search/search/',
                params: {
                    type: 'tags_tag',
                },
                isArray: true,
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);
                    var objects = [];
                    if (jsonData && jsonData.hits && jsonData.hits.length > 0) {
                        jsonData.hits.forEach(function(obj) {
                            objects.push(obj);
                        });
                    }
                    return objects;
                },
            },
            search: {
                url: '/search/search/?type=tags_tag&facet_field=name_flat&facet_filter=name::query&size=0',
                isArray: true,
                transformResponse: function(response) {
                    var data = angular.fromJson(response);
                    var objects = [];
                    if (data && data.facets && data.facets.length > 0) {
                        data.facets.forEach(function(obj) {
                            objects.push({
                                'name': obj.term,
                                'count': obj.count,
                            });
                        });
                    }
                    return objects;
                },
            },
        }
    );

    return _tag;
}
