/**
 * lilyApp Module is the entry point for Lily related Angular code
 */
angular.module('lilyApp', [
    'accountControllers',
    'caseControllers',
    'contactControllers',
    'dealControllers',

    // global modules
    'lilyDirectives',
    'lilyFilters',
    'lilyServices'
]);
