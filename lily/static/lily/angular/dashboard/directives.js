/**
 * dashboardDirectives is a container for all dashboard related Angular directives
 */
angular.module('dashboardDirectives', [])

.directive('unreadEmail', function(){
        return {
            templateUrl: 'dashboard/unreademail.html',
            controller: 'UnreadEmailController'
        }
    });
