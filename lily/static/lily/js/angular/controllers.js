/**
 * caseControllers is a container for all case related Controllers
 */
var LilyApp = angular.module('lilyControllers', []);

LilyApp.config(['$stateProvider', function($stateProvider) {
    $stateProvider.state('base', {
        abstract: true,
        controller: 'baseController',
        views: {
            'topNavActions@': {
                templateUrl: 'top-nav/actions.html',
                controller: 'topNavActionsController'
            },
            'topNavSearch@': {
                templateUrl: 'top-nav/search.html',
                controller: 'topNavSearchController'
            },
            'topNavUser@': {
                templateUrl: 'top-nav/user.html',
                controller: 'topNavUserController'
            },
            'sidebar@': {
                templateUrl: 'sidebar.html',
                controller: 'sidebarController'
            },
            'pageHeader@': {
                templateUrl: 'page-header.html',
                controller: 'pageHeaderController'
            }
        }
    });
}]);

/**
     * CaseListController controller to show list of cases
     *
     */
LilyApp.controller('baseController', [
    '$scope',

    function($scope, $state) {
        $scope.conf = {
            pageTitleBig: 'HelloLily',
            pageTitleSmall: 'welcome to my humble abode!'
        };

        //$scope.$on('$stateChangeStart', function(event, toState, toParams, fromState, fromParams) {
        //    console.log('Starting the state change');
        //});
        //
        //$scope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams) {
        //    console.log('The state has been changed');
        //});

        $scope.$on('$viewContentLoaded', function(event, test, test2) {
            HLSelect2.init();
            HLFormsets.init();
            HLShowAndHide.init();
        });
    }
]);

LilyApp.controller('topNavActionsController', [
    '$scope',

    function($scope) {}
]);

LilyApp.controller('topNavSearchController', [
    '$scope',

    function($scope) {}
]);

LilyApp.controller('topNavUserController', [
    '$scope',

    function($scope) {}
]);
lilyapp.controller('sidebarController', [
    '$scope',

    function($scope) {}
]);

LilyApp.controller('pageHeaderController', [
    '$scope',

    function($scope) {}
]);


