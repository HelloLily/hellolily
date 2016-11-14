angular.module('app.filters').filter('hlTruncate', hlTruncate);

/**
 * Truncate the title with a certain amount of characters based upon the window width.
 *
 * @param title {string}: String that has to be truncated
 */
hlTruncate.$inject = ['$filter'];
function hlTruncate($filter) {
    return function(title) {
        var filteredTitle;
        var ellipsis;
        // Values on which the container goes multiline and overflows the buttons.
        if (window.outerWidth <= 1180) {
            filteredTitle = $filter('limitTo')(title, 30);
            ellipsis = (title.length > 30) ? '...' : '';
        } else if (window.outerWidth <= 1596 && window.outerWidth >= 1180) {
            filteredTitle = $filter('limitTo')(title, 50);
            ellipsis = (title.length > 50) ? '...' : '';
        } else {
            filteredTitle = $filter('limitTo')(title, 100);
            ellipsis = (title.length > 100) ? '...' : '';
        }

        return filteredTitle + ellipsis;
    };
}
