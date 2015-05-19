(function() {
    'use strict';

    /**
     * Contact detail widget
     */
    angular.module('app.contacts.directives').directive('contactDetailWidget', ContactDetailWidget);

    function ContactDetailWidget() {
        return {
            restrict: 'E',
            replace: true,
            scope: {
                contact: '=',
                height: '='
            },
            templateUrl: 'contacts/directives/detail-widget.html'
        }
    }
})();
