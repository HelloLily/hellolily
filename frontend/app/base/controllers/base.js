angular.module('app.base').config(appConfig);

appConfig.$inject = ['$stateProvider'];
function appConfig ($stateProvider) {
    $stateProvider.state('base', {
        abstract: true,
        controller: BaseController,
        ncyBreadcrumb: {
            label: 'Lily'
        }
    });
}

angular.module('app.base').controller('BaseController', BaseController);

BaseController.$inject = ['$scope', '$state', 'Notifications'];
function BaseController ($scope, $state, Notifications) {
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
