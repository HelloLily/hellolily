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
    'CaseControllers',
    'ContactsControllers',
    'AccountControllers',
    'dashboardControllers',
    'DealControllers',
    'EmailControllers',
    'UtilsControllers',

    // Directives
    'lilyDirectives',

    // Google Analytics
    'angulartics',
    'angulartics.google.analytics',

    // Services
    'LilyServices',

    // Filters
    'LilyFilters'
]);

/* Setup global settings */
lilyApp.factory('settings', ['$rootScope', function($rootScope) {
    // supported languages
    var settings = {
        layout: {
            pageSidebarClosed: false // sidebar state
        }
    };

    $rootScope.settings = settings;

    return settings;
}]);

lilyApp.config([
    '$breadcrumbProvider',
    '$controllerProvider',
    '$httpProvider',
    '$resourceProvider',
    '$urlRouterProvider',
    function(
        $breadcrumbProvider,
        $controllerProvider,
        $httpProvider,
        $resourceProvider,
        $urlRouterProvider
    ){
        // Don't strip trailing slashes from calculated URLs, because django needs them
        $breadcrumbProvider.setOptions({
            templateUrl: 'breadcrumbs.html'
        });
        $controllerProvider.allowGlobals();
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        $resourceProvider.defaults.stripTrailingSlashes = false;
        $urlRouterProvider.otherwise('/');
    }
]);

/* Init global settings and run the app */
lilyApp.run(["$rootScope", "settings", "$state", function($rootScope, settings, $state) {
    $rootScope.$state = $state; // state to be accessed from view
    $rootScope.currentUser = currentUser;
}]);
