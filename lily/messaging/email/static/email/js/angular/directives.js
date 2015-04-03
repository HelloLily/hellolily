/**
 * lilyDirectives is a container for all global lily related Angular directives
 */
var EmailDirectives = angular.module('EmailDirectives', []);

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
EmailDirectives.directive('contactIcon', [
    '$http',
    '$modal',
    function($http, $modal) {
        return {
            restrict: 'A',
            scope: {
                message: '='
            },
            replace: true,
            templateUrl: 'email/directives/contact-icon.html',
            link: function(scope, element, attrs) {

                // Do we have an associated account or contact?
                $http.get('/search/emailaddress/' + scope.message.sender_email)
                    .success(function(data) {
                        scope.emailAddressResults = data;
                        if (data.type == 'contact') {

                            scope.icon = 'check';
                            // Contact and has account
                            if (data.data.account) {
                                scope.color = 'green';

                            // Contact without account
                            } else {
                                scope.action = 'needsAccount';
                                scope.icon = 'building'
                                scope.color = 'yellow';
                            }
                        }else if (data.type == 'account') {

                            // Account without contact
                            if (data.complete) {
                                scope.action = 'needsContact';
                                scope.icon = 'user';
                                scope.color = 'blue';

                            // Account with matching domain
                            } else {
                                scope.action = 'needsContact';
                                scope.icon = 'user';
                                scope.color = 'blue';
                            }
                        } else {
                            scope.action = 'needsEverything';
                            scope.icon = 'everything';
                            scope.color = 'grey';
                        }
                    });

                // TODO: Create modal
                //scope.openModal = function() {
                //    $modal.open({
                //        templateUrl: '/static/lily/angular/email/templates/contact-modal.html',
                //        controller: 'ContactModalController',
                //        size: 'lg',
                //        resolve: {
                //            action: function() {
                //                return scope.action;
                //            },
                //            emailAddressResults: function () {
                //                return scope.emailAddressResults;
                //            },
                //            message: function() {
                //                return scope.message;
                //            }
                //        }
                //    });
                //}
            }
        };
    }]
);

// TODO: create modal
//
//
//EmailDirectives.controller('ContactModalController', [
//    '$scope',
//    '$modalInstance',
//    '$http',
//
//    'action',
//    'emailAddressResults',
//    'message',
//    function($scope, $modalInstance, $http, action, emailAddressResults, message) {
//
//        $scope.account = {};
//
//        if (action == 'needsEverything') {
//            $scope.account.url = 'http://www.' + message.sender_email.split('@')[1] + '/';
//        }
//
//        $scope.fetchDomain = function() {
//            console.log($scope.account.url);
//
//            if ($scope.account.url) {
//                var domain = $scope.account.url.replace('http://', '').replace('https://');
//            // Always add last '/'
//            if (domain.slice(-1) !== '/') {
//                domain += '/';
//            }
//
//                $http.get('/provide/account/' + domain)
//                    .success(function(data) {
//                        console.log(data);
//                    });
//            }
//
//        };
//
//        $scope.ok = function () {
//            $modalInstance.close();
//        };
//
//        $scope.cancel = function () {
//            $modalInstance.dismiss();
//        };
//    }]
//);
