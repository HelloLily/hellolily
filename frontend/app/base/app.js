/**
 * App Module is the entry point for Lily related Angular code
 */
angular.module('app', [
    'angular.filter',
    'ui.router',
    'ui.bootstrap',
    'ngResource',
    'ngSanitize',
    'ncy-angular-breadcrumb',
    'multi-transclude',
    'xeditable',
    'angular-cache',

    // Modules
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
    'app.tenants',

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

angular.module('app').config(appConfig);

appConfig.$inject = [
    '$breadcrumbProvider',
    '$controllerProvider',
    '$httpProvider',
    '$resourceProvider',
    '$urlRouterProvider',
];
function appConfig($breadcrumbProvider, $controllerProvider, $httpProvider, $resourceProvider, $urlRouterProvider) {
    // Don't strip trailing slashes from calculated URLs, because Django needs them.
    $breadcrumbProvider.setOptions({
        templateUrl: 'base/breadcrumbs.html',
        includeAbstract: true,
    });
    $controllerProvider.allowGlobals();
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    $resourceProvider.defaults.stripTrailingSlashes = false;
    $urlRouterProvider.otherwise('/');
}

/* Init global settings and run the app. */
angular.module('app').run(runApp);

runApp.$inject = ['$rootScope', '$state', 'editableOptions', 'HLMessages', 'Tenant', 'UserTeams'];
function runApp($rootScope, $state, editableOptions, HLMessages, Tenant, UserTeams) {
    $rootScope.$state = $state; // State to be accessed from view.
    $rootScope.currentUser = currentUser;
    $rootScope.messages = HLMessages;

    // Get tenant name to set custom dimension for GA.
    Tenant.query({}, function(tenant) {
        ga('set', 'dimension1', tenant.name);
    });

    // Get team name to set custom dimension for GA.
    UserTeams.mine(function(teams) {
        if (teams[0]) {
            ga('set', 'dimension2', teams[0].name);
        }
    });

    editableOptions.theme = 'bs3';
}
