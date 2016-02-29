/**
 * contactIcon Directive shows how the email is connected with an account or contact
 *
 * @param message object: object with message info
 *
 * Example:
 *
 * <td contact-icon message="message"></td>
 *
 */
angular.module('app.email.directives').directive('contactIcon', contactIcon);

contactIcon.$inject = ['$http'];
function contactIcon($http) {
    return {
        restrict: 'A',
        scope: {
            message: '=',
        },
        replace: true,
        templateUrl: 'email/directives/contact_icon.html',
        link: function(scope, element, attrs) {
            // Do we have an associated account or contact?
            if (scope.message.sender_email) {
                $http.get('/search/emailaddress/' + scope.message.sender_email, {cache: true})
                    .success(function(data) {
                        scope.emailAddressResults = data;
                        if (data.type === 'contact') {
                            // Contact and has account
                            if (data.data.accounts) {
                                scope.status = 'complete';
                                // Contact without account
                            } else {
                                scope.status = 'needsAccount';
                            }
                        } else if (data.type === 'account') {
                            // Is the emailadress from the account it self (eg. info@)
                            if (data.complete) {
                                scope.status = 'complete';
                            } else {
                                scope.status = 'needsContact';
                            }
                        } else {
                            scope.status = 'needsEverything';
                        }
                    });
            } else {
                scope.status = 'complete';
            }
        },
    };
}
