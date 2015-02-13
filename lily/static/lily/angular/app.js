/**
 * lilyApp Module is the entry point for Lily related Angular code
 */
angular.module('lilyApp', [
    'accountControllers',
    'caseControllers',
    'contactControllers',
    'dealControllers',
    'emailControllers',

    // global modules
    'lilyDirectives',
    'lilyFilters',
    'lilyServices'
]).config(['$resourceProvider', function($resourceProvider) {
  // Don't strip trailing slashes from calculated URLs
  $resourceProvider.defaults.stripTrailingSlashes = false;
}]);
