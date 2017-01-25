angular.module('app.services').factory('HLSearch', HLSearch);

HLSearch.$inject = ['$injector', 'Tag'];
function HLSearch($injector, Tag) {
    HLSearch.refreshList = refreshList;
    HLSearch.refreshTags = refreshTags;
    HLSearch.getOpenCasesDeals = getOpenCasesDeals;

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

    function refreshTags(searchQuery, object, type) {
        var tagsPromise;
        var i;

        var tags = object.tags;
        var contentTypeQuery = 'content_type.name:' + type;
        var query = searchQuery + ',' + contentTypeQuery;
        var filterquery = contentTypeQuery;

        // Exclude tags already selected.
        for (i = 0; i < tags.length; i++) {
            filterquery += ' AND NOT name_flat:' + tags[i].name;
        }

        tagsPromise = Tag.search({query: query, filterquery: filterquery});

        return tagsPromise;
    }

    /**
     * Search for open cases or deals belonging to the object's account and/or contact.
     *
     * @param closedStatusQuery {string}: Contains the filterquery string for the open status(es).
     * @param object {Object}: The case or deal that's used for the queries.
     * @param modelName {String}: Specifies if it's a case or deal.
     */
    function getOpenCasesDeals(closedStatusQuery, object, modelName) {
        var filterQuery = closedStatusQuery;

        if (object.id) {
            // Filter out the current case.
            filterQuery += ' AND NOT id: ' + object.id;
        }

        if (object.account && object.contact) {
            filterQuery += ' AND (account.id:' + object.account.id + ' OR (account.id:' + object.account.id + ' AND contact.id:' + object.contact.id + '))';
        } else {
            if (object.account) {
                filterQuery += ' AND account.id:' + object.account.id;
            }

            if (object.contact) {
                filterQuery += ' AND contact.id:' + object.contact.id;
            }
        }

        // Inject the model's service and execute the search query.
        return $injector.get(modelName).search({filterquery: filterQuery}).$promise;
    }

    return HLSearch;
}
