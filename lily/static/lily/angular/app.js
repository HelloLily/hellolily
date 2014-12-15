/**
 * lilyApp Module is the entry point for Lily related Angular code
 */
angular.module('lilyApp', [
    'contactControllers',
    'accountControllers',
    'caseControllers',

    // global modules
    'lilyDirectives',
    'lilyServices',
    'lilyFilters'
]);
