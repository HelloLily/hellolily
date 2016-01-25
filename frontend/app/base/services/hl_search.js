angular.module('app.services').factory('HLSearch', HLSearch);

HLSearch.$inject = ['$injector'];
function HLSearch($injector) {
    HLSearch.refreshList = refreshList;

    function refreshList(query, model, excludeItems, extraQuery) {
        var items = [];

        if (!extraQuery) {
            extraQuery = '';
        }

        // Dynamically get the model.
        model = $injector.get(model);

        if (query.length) {
            // At least 2 characters need to be entered.
            if (query.length >= 2) {
                var exclude = '';

                // Only exclude items if we have a multi-select field.
                if (excludeItems) {
                    // Exclude items already selected.
                    angular.forEach(items, function(item) {
                        exclude += ' AND NOT id:' + item.id;
                    });
                }

                items = model.search({filterquery: 'name:(' + query + ')' + exclude + extraQuery, size: 60, sort: '-modified'});
            }
        } else {
            // No query yet, so just get the last 60 items of the given model.
            items = model.search({filterquery: extraQuery, size: 60, sort: '-modified'});
        }

        return items;
    }

    return HLSearch;
}
