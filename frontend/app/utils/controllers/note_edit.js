angular.module('app.utils').controller('EditNoteModalController', EditNoteModalController);

EditNoteModalController.$inject = ['$http', '$modalInstance', '$scope', 'note'];
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
