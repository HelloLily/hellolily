/**
 * lilyControllers is a container for all global lily related Angular controllers
 */
var UtilsControllers = angular.module('UtilsControllers', []);

UtilsControllers.controller('historyList', EditNoteModalController);

EditNoteModalController.$inject = [
    '$http',
    '$modalInstance',
    '$scope',
    'note'
];
function EditNoteModalController($http, $modalInstance, $scope, note) {
    $scope.note = note;
    $scope.ok = function () {
        $http({
            url: '/notes/update/' + $scope.note.id + '/',
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            data: $.param({content: $scope.note.content, type: $scope.note.type})
        }).success(function() {
            $modalInstance.close($scope.note);
        });
    };

    // Lets not change anything
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
}
