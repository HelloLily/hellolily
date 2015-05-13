(function() {
    'use strict';

    /**
     * Account detail widget
     */
    angular.module('app.accounts.directives').directive('accountDetailWidget', AccountDetailWidget);

    function AccountDetailWidget() {
        return {
            restrict: 'E',
            replace: true,
            scope: {
                account: '=',
                height: '='
            },
            templateUrl: 'accounts/directives/detail-widget.html'
        }
    }
})();
