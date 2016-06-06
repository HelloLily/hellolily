angular.module('app.utils').controller('EditNoteModalController', EditNoteModalController);

EditNoteModalController.$inject = ['$uibModalInstance', 'HLForms', 'HLUtils', 'Note', 'note'];
function EditNoteModalController($uibModalInstance, HLForms, HLUtils, Note, note) {
    var vm = this;
    vm.note = note;
    vm.ok = ok;
    vm.cancel = cancel;

    activate();

    ///////////////////

    function activate() {
        vm.note.modalType = note.type;
        vm.note.content = HLUtils.decodeHtmlEntities(vm.note.content);
    }

    function ok(form) {
        // Use the Note resource for updating the content attribute.
        Note.update({id: vm.note.id}, {id: vm.note.id, content: vm.note.content}, function() {
            // Success.
            $uibModalInstance.close();
            toastr.success('I\'ve updated the note for you!', 'Done');
        }, function(response) {
            // Error.
            HLForms.setErrors(form, response.data);
            toastr.error('Uh oh, there seems to be a problem', 'Oops!');
        });
    }

    // Lets not change anything
    function cancel() {
        $uibModalInstance.dismiss('cancel');
    }
}
