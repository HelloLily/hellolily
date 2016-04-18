angular.module('app.services').factory('HLSearch', HLSearch);

HLSearch.$inject = ['$injector'];
function HLSearch($injector) {
    HLSearch.refreshList = refreshList;

    function refreshList(query, modelName, excludeItems, extraFilterQuery) {
        var items;
        var sort;
        var nameFilter;
        var exclude = '';

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
                if (excludeItems) {
                    // Exclude items already selected.
                    angular.forEach(excludeItems, function(item) {
                        exclude += ' AND NOT id:' + item.id;
                    });
                }

                items = model.search({filterquery: nameFilter + ':(' + query + ')' + exclude + extraQuery, size: 60, sort: sort});
            }
        } else {
            // No query yet, so just get the last 60 items of the given model.
            items = model.search({filterquery: extraQuery, size: 60, sort: sort});
        }

        return items;
    }

    return HLSearch;
}
