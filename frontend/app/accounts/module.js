/**
 * app.accounts manages all routes, controllers eg.
 * that relate to Account.
 */
angular.module('app.accounts', [
    'ngCookies',
    'ui.bootstrap',
    'ui.slimscroll',
    'app.accounts.services',
    'app.cases.services',
    'app.email.services',
    'app.contacts.services',
    'noteServices'
]);
