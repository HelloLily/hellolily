angular.module('app.utils.directives').directive('historyAddNote', historyAddNoteDirective);

function historyAddNoteDirective() {
    return {
        restrict: 'E',
        scope: {
            item: '=',
        },
        templateUrl: 'utils/directives/history_add_note.html',
        controller: HistoryAddNoteController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

HistoryAddNoteController.$inject = ['$http', '$state', 'Note'];
function HistoryAddNoteController($http, $state, Note) {
    var vm = this;
    vm.note = new Note({content_type: vm.item.content_type, object_id: vm.item.id, type: 0});

    vm.addNote = addNote;

    function addNote() {
        vm.note.$save(function(response) {
            console.log(response);
            vm.item.notes.unshift(response);
            // 'Empty' the note object to be able to continue posting another
            // note without having to refresh the page.
            vm.note = new Note({content_type: vm.item.content_type, object_id: vm.item.id, type: 0});
        });
    }
}
