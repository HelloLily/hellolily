angular.module('app.utils.directives').directive('activityAddNote', activityAddNoteDirective);

function activityAddNoteDirective() {
    return {
        restrict: 'E',
        scope: {
            item: '=',
        },
        templateUrl: 'utils/directives/activity_stream_add_note.html',
        controller: ActivityAddNoteController,
        controllerAs: 'vm',
        bindToController: true,
        link: (scope, element, attrs) => {
            element[0].focus();
        },
    };
}

ActivityAddNoteController.$inject = ['$http', '$state', 'Note', 'User'];
function ActivityAddNoteController($http, $state, Note, User) {
    let vm = this;

    let contentType = vm.item.content_type;

    if (typeof vm.item.content_type === 'object') {
        contentType = vm.item.content_type.id;
    }

    vm.note = new Note({gfk_content_type: contentType, gfk_object_id: vm.item.id, type: 0});

    vm.addNote = addNote;

    function addNote() {
        if (vm.note.content) {
            vm.note.$save(response => {
                // Set user object to note to correctly show profile pic and name
                // when adding a new note in the activity stream.
                User.get({id: currentUser.id}, author => {
                    response.author = author;
                });

                vm.item.notes.unshift(response);
                // 'Empty' the note object to be able to continue posting another
                // note without having to refresh the page.
                vm.note = new Note({gfk_content_type: vm.item.content_type, gfk_object_id: vm.item.id, type: 0});
            });
        } else {
            toastr.error('You can\'t create an empty note!', 'Oops!');
        }
    }
}
