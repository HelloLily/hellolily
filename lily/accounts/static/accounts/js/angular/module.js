(function() {
    'use strict';

    /**
     * app.account manages all routes, controllers eg.
     * that relate to Account.
     */
    angular.module('app.accounts', [
        'ngCookies',
        'ui.bootstrap',
        'ui.slimscroll',
        'AccountServices',
        'CaseServices',
        'contactServices',
        'noteServices',
        'app.email.services'
    ]);
})();
