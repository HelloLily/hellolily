/**
 * lilyApp Module is the entry point for Lily related Angular code
 */
var lilyApp = angular.module('lilyApp', [
    'accountControllers',
    'caseControllers',
    'contactControllers',
    'dashboardControllers',
    'dealControllers',
    'emailControllers',

    // global modules
    'lilyDirectives',
    'lilyFilters',
    'lilyServices'
]);

lilyApp.config(['$resourceProvider', function($resourceProvider) {
  // Don't strip trailing slashes from calculated URLs
  $resourceProvider.defaults.stripTrailingSlashes = false;
}]);
