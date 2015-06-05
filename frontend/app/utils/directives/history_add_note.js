angular.module('app.utils.directives').directive('historyAddNote', historyAddNoteDirective);

function historyAddNoteDirective () {
    return {
        restrict: 'E',
        scope: {
            item: '='
        },
        templateUrl: 'utils/controllers/history_add_note.html',
        controller: HistoryAddNoteController,
        controllerAs: 'vm',
        bindToController: true
    }
}

HistoryAddNoteController.$inject = ['$http', '$state'];
function HistoryAddNoteController ($http, $state) {
    var vm = this;

    vm.addNote = addNote;

    //////

    function addNote () {
        $http({
            method: 'POST',
            url: '/notes/create/',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            data: $.param({
                content: vm.note,
                type: 0,
                content_type: vm.item.historyType,
                object_id: vm.item.id
            })
        }).success(function() {
            $state.go($state.current, {}, {reload: true});
        });
    }
}
