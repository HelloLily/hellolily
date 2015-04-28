(function(){
    'use strict';

    /**
     * lilyApp Module is the entry point for Lily related Angular code
     */
    angular.module('lilyApp', [
        'ui.router',
        'ngResource',
        'ngSanitize',
        'ncy-angular-breadcrumb',

        // Controllers
        'app.accounts',
        'app.email',
        'app.preferences',
        'app.preferences.email',
        'app.preferences.user',
        'lilyControllers',
        'CaseControllers',
        'ContactsControllers',
        'dashboardControllers',
        'DealControllers',

        // Directives
        'CaseDirectives',
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
    angular.module('lilyApp').factory('settings', ['$rootScope', function($rootScope) {
        // supported languages
        var settings = {
            layout: {
                pageSidebarClosed: false // sidebar state
            }
        };

        $rootScope.settings = settings;

        return settings;
    }]);

    angular.module('lilyApp').config([
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
                templateUrl: 'breadcrumbs.html',
                includeAbstract: true
            });
            $controllerProvider.allowGlobals();
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
            $resourceProvider.defaults.stripTrailingSlashes = false;
            $urlRouterProvider.otherwise('/');
        }
    ]);

    /* Init global settings and run the app */
    angular.module('lilyApp').run(['$rootScope', 'settings', '$state', function($rootScope, settings, $state) {
        $rootScope.$state = $state; // state to be accessed from view
        $rootScope.currentUser = currentUser;
    }]);
})();
