angular.module('app.utils.directives').directive('historyAddNote', historyAddNoteDirective);

function historyAddNoteDirective () {
    return {
        restrict: 'E',
        scope: {
            item: '='
        },
        templateUrl: 'utils/directives/history_add_note.html',
        controller: HistoryAddNoteController,
        controllerAs: 'vm',
        bindToController: true
    }
}

HistoryAddNoteController.$inject = ['$http', '$state'];
function HistoryAddNoteController ($http, $state) {
    var vm = this;

    vm.addNote = addNote;
    vm.type = 0;
    //////

    function addNote () {



        $http({
            method: 'POST',
            url: '/notes/create/',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            data: $.param({
                content: vm.note,
                type: vm.type,
                content_type: vm.item.historyType,
                object_id: vm.item.id
            })
        }).success(function() {
            $state.go($state.current, {}, {reload: true});
        });
    }
}
