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
    'dashboardControllers',

    // global modules
    'lilyDirectives',
    'lilyFilters',
    'lilyServices'
]);

/* Setup global settings */
lilyApp.factory('settings', ['$rootScope', function($rootScope) {
    // supported languages
    var settings = {
        layout: {
            pageSidebarClosed: false, // sidebar state
            pageAutoScrollOnLoad: 1000 // auto scroll to top on page load
        }
    };

    $rootScope.settings = settings;

    return settings;
}]);

lilyApp.config([
    '$urlRouterProvider',
    '$resourceProvider',
    '$breadcrumbProvider',
    '$controllerProvider',

    function(
        $urlRouterProvider,
        $resourceProvider,
        $breadcrumbProvider,
        $controllerProvider
    ){
        // Don't strip trailing slashes from calculated URLs, because django needs them
        $resourceProvider.defaults.stripTrailingSlashes = false;
        $urlRouterProvider.otherwise('/');
        $breadcrumbProvider.setOptions({
            templateUrl: 'breadcrumbs.html'
        });
        $controllerProvider.allowGlobals();
    }
]);

/* Init global settings and run the app */
lilyApp.run(["$rootScope", "settings", "$state", function($rootScope, settings, $state) {
    $rootScope.$state = $state; // state to be accessed from view
}]);
