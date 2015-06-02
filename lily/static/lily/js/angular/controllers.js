(function() {
    'use strict';

    angular.module('app.base', ['ui.bootstrap']).config(baseConfig);

    baseConfig.$inject = ['$stateProvider'];
    function baseConfig($stateProvider){
        $stateProvider.state('base', {
            abstract: true,
            controller: 'baseController',
            ncyBreadcrumb: {
                label: 'Lily'
            }
        });
    }

    angular.module('app.base').controller('baseController', baseController);

    baseController.$inject = ['$http', '$scope', '$state', 'Notifications'];
    function baseController($http, $scope, $state, Notifications){
        $scope.conf = {
            headTitle: 'Welcome!',
            pageTitleBig: 'HelloLily',
            pageTitleSmall: 'welcome to my humble abode!'
        };

        $scope.loadNotifications = loadNotifications;

        activate();

        //////////

        function activate(){
            $scope.$on('$stateChangeSuccess', _setPreviousState);
            $scope.$on('$viewContentLoaded', _contentLoadedActions);
        }

        function loadNotifications() {
            Notifications.query(function(notifications) {  // On success
                angular.forEach(notifications, function(message) {
                    toastr[message.level](message.message);
                });
            }, function(error) {  // On error
                console.log('error!');
                console.log(error);
            })
        }

        function _contentLoadedActions() {
            Metronic.initComponents(); // init core components
            HLSelect2.init();
            HLFormsets.init();
            HLShowAndHide.init();
            autosize($('textarea'));

            $scope.loadNotifications();
        }

        function _setPreviousState(event, toState, toParams, fromState, fromParams){
            $scope.previousState = $state.href(fromState, fromParams);
        }
    }

    angular.module('app.base').controller('headerController', headerController);

    headerController.$inject = ['$scope'];
    function headerController($scope){
        $scope.$on('$includeContentLoaded', initHeader);

        //////////

        function initHeader(){
            Layout.initHeader();
        }
    }

    angular.module('app.base').controller('sidebarController', sidebarController);

    sidebarController.$inject = ['$scope'];
    function sidebarController($scope){
        $scope.$on('$includeContentLoaded', initSidebar);

        //////////

        function initSidebar(){
            Layout.initSidebar();
        }
    }
})();
