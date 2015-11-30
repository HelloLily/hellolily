/**
 * stripScheme strips the scheme of the given URL (e.g. http://).
 *
 * @param url {string}: String containing the URL
 *
 * @returns: string: The stripped URL
 */
angular.module('app.filters').filter('stripScheme', stripScheme);

stripScheme.$inject = [];
function stripScheme() {
    return function(url) {
        return url.replace(/http(s)?:\/\//, '');
    };
}
