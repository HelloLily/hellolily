/**
 * caseControllers is a container for all case related Controllers
 */
var lilyControllers = angular.module('lilyControllers', [
    'ui.bootstrap'
]);

lilyControllers.config(['$stateProvider', function($stateProvider) {
    $stateProvider.state('base', {
        abstract: true,
        controller: 'baseController'
    });
}]);

/**
 * BaseController is the controller where all the default things are loaded
 *
 */
lilyControllers.controller('baseController', [
    '$http',
    '$scope',
    '$state',
    '$modal',
    'Notifications',

    function($http, $scope, $state, $modal, Notifications) {
        $scope.conf = {
            headTitle: 'Welcome!',
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

        $scope.$on('$viewContentLoaded', function() {
            Metronic.initComponents(); // init core components
            HLSelect2.init();
            HLFormsets.init();
            HLShowAndHide.init();

            // Get notifications
            Notifications.query(function(notifications) {  // On success
                angular.forEach(notifications, function(message) {
                    toastr[message.level](message.message);
                });
            }, function(error) {  // On error
                console.log('error!');
                console.log(error);
            })
        });

        $scope.editNote = function(note) {
            var modalInstance = $modal.open({
                templateUrl: 'notes/edit.html',
                controller: 'EditNoteModalController',
                size: 'lg',
                resolve: {
                        note: function() {
                            return note;
                        }
                }
            });

            modalInstance.result.then(function() {
                $state.go($state.current, {}, {reload: true});
            }, function () {
            });
        };

        /**
         * Add note to the historylist
         */
        $scope.addNote =function(contentType, objectId, content) {
            $http({
                method: 'POST',
                url: '/notes/create/',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                data: $.param({
                    content: content,
                    content_type: contentType,
                    object_id: objectId
                })
            }).success(function() {
                $state.go($state.current, {}, {reload: true});
            });
        };
    }
]);

lilyControllers.controller('headerController', [
    '$scope',

    function($scope) {
        $scope.$on('$includeContentLoaded', function() {
            Layout.initHeader(); // init header
        });
    }
]);

lilyControllers.controller('sidebarController', [
    '$scope',

    function($scope) {
        $scope.$on('$includeContentLoaded', function() {
            Layout.initSidebar(); // init sidebar
        });
    }
]);

/**
 * EditNoteModalController is a controller to edit a note.
 */
lilyControllers.controller('EditNoteModalController', [
    '$http',
    '$modalInstance',
    '$scope',
    'note',
    function($http, $modalInstance, $scope, note) {
        $scope.note = note;
        $scope.ok = function () {
            $http({
                url: '/notes/update/' + $scope.note.id + '/',
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                data: $.param({content: $scope.note.content})
            }).success(function() {
                $modalInstance.close($scope.note);
            });
        };

        // Lets not change anything
        $scope.cancel = function () {
            $modalInstance.dismiss('cancel');
        };
    }
]);
