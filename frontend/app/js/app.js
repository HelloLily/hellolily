/**
 * lilyApp Module is the entry point for Lily related Angular code
 */
angular.module('lilyApp', [
    'ui.router',
    'ui.bootstrap',
    'ngResource',
    'ngSanitize',
    'ncy-angular-breadcrumb',

    // Controllers
    'app.accounts',
    'app.base',
    'app.cases',
    'app.dashboard',
    'app.email',
    'app.preferences',
    'app.preferences.email',
    'app.preferences.user',
    'app.templates',
    'ContactsControllers',
    'DealControllers',
    'UtilsControllers',

    // Directives
    'app.directives',
    'app.accounts.directives',
    'app.cases.directives',
    'app.contacts.directives',
    'app.deals.directives',
    'UtilsDirectives',

    // Google Analytics
    'angulartics',
    'angulartics.google.analytics',

    // Services
    'app.services',

    // Filters
    'app.filters'
]);

/* Setup global settings */
angular.module('lilyApp').factory('settings', settings);

settings.$inject = ['$rootScope'];
function settings ($rootScope) {
    // supported languages
    var settings = {
        layout: {
            pageSidebarClosed: false // sidebar state
        }
    };

    $rootScope.settings = settings;

    return settings;
}

angular.module('lilyApp').config(lilyAppConfig);

lilyAppConfig.$inject = [
    '$breadcrumbProvider',
    '$controllerProvider',
    '$httpProvider',
    '$resourceProvider',
    '$urlRouterProvider'
];
function lilyAppConfig ($breadcrumbProvider, $controllerProvider, $httpProvider, $resourceProvider, $urlRouterProvider){
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

/* Init global settings and run the app */
angular.module('lilyApp').run(runApp);

runApp.$inject = ['$rootScope', 'settings', '$state'];
function runApp ($rootScope, $state) {
    $rootScope.$state = $state; // state to be accessed from view
    $rootScope.currentUser = currentUser;
}
