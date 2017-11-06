// Include libraries.
var Raven = require('raven-js');

window.sprintf = require('sprintf-js').sprintf;
window.moment = require('moment');

require('angular-xeditable');
require('angular-ui-bootstrap');
require('sweetalert2');
require('angular-elastic');
require('ui-select');

/**
 * App Module is the entry point for Lily related Angular code
 */
angular.module('app', [
    'angular.filter',
    'ui.router',
    'ui.bootstrap',
    'ui.select',
    'ngResource',
    'ngSanitize',
    'ncy-angular-breadcrumb',
    'xeditable',
    'angular-cache',
    'ngFileUpload',
    'monospaced.elastic',

    // Modules
    'app.accounts',
    'app.base',
    'app.calls',
    'app.cases',
    'app.changes',
    'app.contacts',
    'app.dashboard',
    'app.deals',
    'app.email',
    'app.integrations',
    'app.preferences',
    'app.stats',
    'app.tags',
    'app.templates',
    'app.utils',
    'app.tenants',
    'app.timelogs',

    // Directives
    'app.directives',
    'app.accounts.directives',
    'app.cases.directives',
    'app.contacts.directives',
    'app.deals.directives',
    'app.timelogs.directives',
    'app.utils.directives',
    'app.preferences.email.directives',

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

    swal.setDefaults({
        confirmButtonClass: 'hl-primary-btn-blue',
        cancelButtonClass: 'hl-primary-btn',
        buttonsStyling: false,
    });
}

// Global exception handler.
angular.module('app').factory('$exceptionHandler', ['$log', $log => {
    return exception => {
        $log.error(exception);

        if (!window.debug) {
            // Also send to Sentry if debug is off.
            Raven.captureException(exception);
        }
    };
}]);

/* Init global settings and run the app. */
angular.module('app').run(runApp);

runApp.$inject = ['$rootScope', '$state', 'editableOptions', 'HLMessages', 'HLSockets', 'HLNotifications', 'Tenant', 'UserTeams'];
function runApp($rootScope, $state, editableOptions, HLMessages, HLSockets, HLNotifications, Tenant, UserTeams) {
    $rootScope.$state = $state; // State to be accessed from view.
    $rootScope.currentUser = currentUser;
    $rootScope.messages = HLMessages;
    window.messages = HLMessages;

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

    new window.Intercom('boot', {
        app_id: intercomAppId,
        user_id: currentUser.id,
        name: currentUser.fullName,
        email: currentUser.email,
        company: {
            name: currentUser.company,
            id: currentUser.tenant.id,
        },
        widget: {
            activator: '#IntercomDefaultWidget',
        },
        user_hash: currentUser.user_hash,
    });

    // Only setup if we're in the live app.
    if (!window.debug) {
        // Setup Raven for global JS error logging.
        Raven.config(window.sentryPublicDsn).addPlugin(require('raven-js/plugins/angular'), angular).install();
        Raven.setUserContext({
            id: currentUser.id,
        });
    }
}
