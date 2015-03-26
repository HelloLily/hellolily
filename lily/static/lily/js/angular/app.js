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
    'dashboardControllers',
    'DealControllers',
    'EmailControllers',
    'UtilsControllers',

    // global modules
    'lilyDirectives',
    'lilyFilters',
    'LilyServices'
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
        $resourceProvider.defaults.stripTrailingSlashes = false;
        $urlRouterProvider.otherwise('/');
        $breadcrumbProvider.setOptions({
            templateUrl: 'breadcrumbs.html'
        });
        $controllerProvider.allowGlobals();

        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    }
]);

/* Init global settings and run the app */
lilyApp.run(["$rootScope", "settings", "$state", function($rootScope, settings, $state) {
    $rootScope.$state = $state; // state to be accessed from view
}]);
