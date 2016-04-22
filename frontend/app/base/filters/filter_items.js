angular.module('app.filters').filter('filterItems', filterItems);

filterItems.$inject = ['$filter'];
function filterItems($filter) {
    return function(items, existingItems) {
        var i;
        var out = items;

        if (items && existingItems) {
            // Filter given items based on already existing items.
            for (i = 0; i < existingItems.length; i++) {
                out = $filter('removeWith')(out, {id: existingItems[i].id});
            }
        }

        return out;
    };
}
