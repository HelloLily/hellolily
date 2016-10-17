angular.module('app.services').factory('HLSearch', HLSearch);

HLSearch.$inject = ['$injector', 'Tag'];
function HLSearch($injector, Tag) {
    HLSearch.refreshList = refreshList;
    HLSearch.refreshTags = refreshTags;

    function refreshList(query, modelName, extraFilterQuery, sortColumn = '-modified', nameColumn = 'name') {
        var items;

        // Dynamically get the model.
        var model = $injector.get(modelName);

        var extraQuery = extraFilterQuery ? extraFilterQuery : '';

        if (query.length) {
            // At least 2 characters need to be entered.
            if (query.length >= 2) {
                // Only exclude items if we have a multi-select field.
                items = model.search({
                    filterquery: nameColumn + ':(' + query + ')' + extraQuery,
                    size: 60,
                    sort: sortColumn,
                });
            }
        } else {
            // No query yet, so just get the last 60 items of the given model.
            items = model.search({filterquery: extraQuery, size: 60, sort: sortColumn});
        }

        return items;
    }

    function refreshTags(query, tags) {
        var exclude = '';
        var tagsPromise;
        var i;

        // Exclude tags already selected.
        for (i = 0; i < tags.length; i++) {
            if (i === 0) {
                exclude += 'NOT name_flat:' + tags[i].name;
            } else {
                exclude += ' AND NOT name_flat:' + tags[i].name;
            }
        }

        tagsPromise = Tag.search({query: query, filterquery: exclude});

        return tagsPromise;
    }

    return HLSearch;
}
