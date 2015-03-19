/**
 * caseControllers is a container for all case related Controllers
 */
angular.module('lilyControllers', [])

    /**
     * CaseListController controller to show list of cases
     *
     */
    .controller('lilyController', [
        '$scope',

        function($scope) {
            console.log('base');
        }
    ])
    .controller('DashboardController', [
        '$scope',

        function($scope) {
            console.log('dashboard');
        }
    ])
    .controller('topNavActionsController', [
        '$scope',

        function($scope) {
            console.log('topnav actions');
        }
    ])
    .controller('topNavSearchController', [
        '$scope',

        function($scope) {
            console.log('topnav search');
        }
    ])
    .controller('topNavUserController', [
        '$scope',

        function($scope) {
            console.log('topnav user');
        }
    ])
    .controller('sidebarController', [
        '$scope',

        function($scope) {
            console.log('sidebar');
        }
    ])
    .controller('pageHeaderController', [
        '$scope',

        function($scope) {
            console.log('page header');
        }
    ])
    .config(['$stateProvider', function($stateProvider) {
        $stateProvider
            .state('base', {
                abstract: true,
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
            })
            .state('base.dashboard', {
                url: '/dashboard/',
                template: 'dashboard.html',
                controller: 'DashboardController'
            });
    }]);
