angular.module('app.services').factory('HLSearch', HLSearch);

HLSearch.$inject = ['$injector'];
function HLSearch($injector) {
    HLSearch.refreshList = refreshList;
    HLSearch.refreshTags = refreshTags;

    function refreshList(query, modelName, extraFilterQuery) {
        var items;
        var sort;
        var nameFilter;

        // Dynamically get the model.
        var model = $injector.get(modelName);

        var extraQuery = extraFilterQuery ? extraFilterQuery : '';

        // User model is filtered differently, so check if we're dealing with
        // the User model or not.
        if (modelName === 'User') {
            sort = 'full_name';
            nameFilter = 'full_name';
        } else {
            sort = '-modified';
            nameFilter = 'name';
        }

        if (query.length) {
            // At least 2 characters need to be entered.
            if (query.length >= 2) {
                // Only exclude items if we have a multi-select field.
                items = model.search({
                    filterquery: nameFilter + ':(' + query + ')' + extraQuery,
                    size: 60,
                    sort: sort,
                });
            }
        } else {
            // No query yet, so just get the last 60 items of the given model.
            items = model.search({filterquery: extraQuery, size: 60, sort: sort});
        }

        return items;
    }

    function refreshTags(query, tags) {
        var exclude = '';
        var tagsPromise;

        if (query.length >= 1) {
            // Exclude tags already selected.
            angular.forEach(tags, function(tag) {
                exclude += ' AND NOT name_flat:' + tag.name;
            });

            // Just load the 'Tag' model dynamically, so we don't have to
            // inject it into the controller.
            tagsPromise = $injector.get('Tag').search({query: query + exclude});
        }

        return tagsPromise;
    }

    return HLSearch;
}
