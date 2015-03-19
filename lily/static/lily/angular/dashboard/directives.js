/**
 * dashboardDirectives is a container for all dashboard related Angular directives
 */
var dashboard = angular.module('dashboardDirectives', []);

dashboard.directive('unreadEmail', function () {
    return {
        templateUrl: 'dashboard/unreademail.html',
        controller: 'UnreadEmailController'
    }
});

dashboard.directive('myCases', function () {
    return {
        templateUrl: 'dashboard/mycases.html',
        controller: 'MyCasesController'
    }
});

dashboard.directive('callbackRequests', function () {
    return {
        templateUrl: 'dashboard/callbackrequests.html',
        controller: 'CallbackRequestsController'
    }
});
