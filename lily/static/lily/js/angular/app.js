/**
 * lilyApp Module is the entry point for Lily related Angular code
 */
angular.module('lilyApp', [
    'ui.router',
    'ngResource',

    // Controllers
    'lilyControllers',
    'ContactsControllers',

    // global modules
    'lilyDirectives',
    'lilyFilters',
    'lilyServices'
]).config([
    '$urlRouterProvider',
    '$resourceProvider',

    function(
        $urlRouterProvider,
        $resourceProvider)
    {
        // Don't strip trailing slashes from calculated URLs
        $resourceProvider.defaults.stripTrailingSlashes = false;
        $urlRouterProvider.otherwise('/dashboard/');
    }
]);
