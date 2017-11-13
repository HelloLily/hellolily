angular.module('app.services').factory('HLSearch', HLSearch);

HLSearch.$inject = ['$injector', 'Tag'];
function HLSearch($injector, Tag) {
    HLSearch.refreshList = refreshList;
    HLSearch.refreshTags = refreshTags;
    HLSearch.getOpenCasesDeals = getOpenCasesDeals;

    function refreshList(query, modelName, extraFilterQuery, sortColumn = '-modified', nameColumn = 'name') {
        // Dynamically get the model.
        const model = $injector.get(modelName);

        const extraQuery = extraFilterQuery ? extraFilterQuery : '';

        let items;

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
        const tags = object.tags;
        const contentTypeQuery = 'content_type.name:' + type;
        const query = searchQuery + ',' + contentTypeQuery;
        let filterquery = contentTypeQuery;

        if (tags) {
            // Exclude tags already selected.
            for (let i = 0; i < tags.length; i++) {
                filterquery += ' AND NOT name_flat:' + tags[i].name;
            }
        }

        const tagsPromise = Tag.search({query, filterquery});

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
        let filterquery = closedStatusQuery;

        if (object.id) {
            // Filter out the current case.
            filterquery += ` AND NOT id: ${object.id}`;
        }

        if (object.account && object.contact && object.account.id && object.contact.id) {
            filterquery += ` AND (account.id:${object.account.id} OR (account.id:${object.account.id} AND contact.id:${object.contact.id}))`;
        } else {
            if (object.account && object.account.id) {
                filterquery += ` AND account.id:${object.account.id}`;
            }

            if (object.contact && object.contact.id) {
                filterquery += ` AND contact.id: ${object.contact.id}`;
            }
        }

        // Inject the model's service and execute the search query.
        return $injector.get(modelName).search({filterquery}).$promise;
    }

    return HLSearch;
}
