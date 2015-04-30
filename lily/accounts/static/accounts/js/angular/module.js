(function() {
    'use strict';

    /**
     * app.accounts manages all routes, controllers eg.
     * that relate to Account.
     */
    angular.module('app.accounts', [
        'ngCookies',
        'ui.bootstrap',
        'ui.slimscroll',
        'AccountServices',
        'app.cases.services',
        'app.email.services',
        'contactServices',
        'noteServices'
    ]);
})();
