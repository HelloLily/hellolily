angular.module('app.preferences.email.directives').directive('userShare', userShare);

function userShare() {
    return {
        restrict: 'E',
        replace: true,
        templateUrl: 'preferences/email/directives/user_share.html',
    };
}
