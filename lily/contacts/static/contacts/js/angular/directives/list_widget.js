(function() {
    'use strict';

    /**
     * Contacts list widget
     */
    angular.module('app.contacts.directives').directive('contactListWidget', ContactListWidget);

    function ContactListWidget() {
        return {
            restrict: 'E',
            replace: true,
            scope: {
                title: '@',
                list: '=',
                height: '='
            },
            templateUrl: 'contacts/directives/list-widget.html'
        }
    }
})();
