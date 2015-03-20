/**
 * lilyApp Module is the entry point for Lily related Angular code
 */
var lilyApp = angular.module('lilyApp', [
    'ui.router',
    'ngResource',
    'ngSanitize',
    'ncy-angular-breadcrumb',

    // Controllers
    'lilyControllers',
    'ContactsControllers',

    // global modules
    'lilyDirectives',
    'lilyFilters',
    'lilyServices'
]);

lilyApp.config([
    '$urlRouterProvider',
    '$resourceProvider',
    '$breadcrumbProvider',

    function(
        $urlRouterProvider,
        $resourceProvider,
        $breadcrumbProvider
    ){
        // Don't strip trailing slashes from calculated URLs
        $resourceProvider.defaults.stripTrailingSlashes = true;
        $urlRouterProvider.otherwise('/dashboard');
        $breadcrumbProvider.setOptions({
            templateUrl: 'breadcrumbs.html'
        });
    }
]);
