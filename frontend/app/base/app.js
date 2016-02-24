/**
 * App Module is the entry point for Lily related Angular code
 */
angular.module('app', [
    'angular.filter',
    'ui.router',
    'ui.bootstrap',
    'ngAnimate',
    'ngResource',
    'ngSanitize',
    'ncy-angular-breadcrumb',
    'multi-transclude',
    'xeditable',

    // Controllers
    'app.accounts',
    'app.base',
    'app.cases',
    'app.contacts',
    'app.dashboard',
    'app.deals',
    'app.email',
    'app.preferences',
    'app.stats',
    'app.tags',
    'app.templates',
    'app.utils',

    // Directives
    'app.directives',
    'app.accounts.directives',
    'app.cases.directives',
    'app.contacts.directives',
    'app.deals.directives',
    'app.utils.directives',

    // Google Analytics
    'angulartics',
    'angulartics.google.analytics',

    // Services
    'app.services',

    // Filters
    'app.filters',
]);

/* Setup global settings */
angular.module('app').factory('settings', settings);

settings.$inject = ['$rootScope'];
function settings($rootScope) {
    // supported languages
    var settings = {
        layout: {
            pageSidebarClosed: false // sidebar state
        },
    };

    $rootScope.settings = settings;

    return settings;
}

angular.module('app').config(appConfig);

appConfig.$inject = [
    '$animateProvider',
    '$breadcrumbProvider',
    '$controllerProvider',
    '$httpProvider',
    '$resourceProvider',
    '$urlRouterProvider',
];
function appConfig($animateProvider, $breadcrumbProvider, $controllerProvider, $httpProvider,
                   $resourceProvider, $urlRouterProvider) {
    // Don't strip trailing slashes from calculated URLs, because django needs them
    $breadcrumbProvider.setOptions({
        templateUrl: 'base/breadcrumbs.html',
        includeAbstract: true,
    });
    $controllerProvider.allowGlobals();
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    $resourceProvider.defaults.stripTrailingSlashes = false;
    $urlRouterProvider.otherwise('/');
    // prevent ng-animation on fa-spinner
    $animateProvider.classNameFilter(/^((?!(fa-spin)).)*$/);
}

/* Init global settings and run the app */
angular.module('app').run(runApp);

runApp.$inject = ['$rootScope', '$state', 'settings', 'editableOptions'];
function runApp($rootScope, $state, settings, editableOptions) {
    $rootScope.$state = $state; // state to be accessed from view
    $rootScope.currentUser = currentUser;
    $rootScope.settings = settings;

    editableOptions.theme = 'bs3';
}
