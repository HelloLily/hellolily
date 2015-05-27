(function() {
    'use strict';

    /**
     * app.preferences.email is a container for all case related Controllers
     */
    angular.module('app.preferences.email', [
        'ui.bootstrap',
        'ui.slimscroll',
        'app.users.services',
        'app.email.services',
        'app.services',
        'UserFilters'
    ]);
})();
