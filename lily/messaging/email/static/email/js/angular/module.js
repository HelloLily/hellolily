(function() {
    'use strict';

    /**
     * app.email is a container for all email related Controllers
     */
    angular.module('app.email', [
        // 3rd party
        'ui.bootstrap',
        'ui.router',

        // Lily dependencies
        'app.email.services',
        'app.email.directives',
        'app.services'
    ]);
})();
