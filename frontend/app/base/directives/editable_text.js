angular.module('app.directives').directive('editableText', editableText);

function editableText() {
    return {
        restrict: 'E',
        scope: {
            field: '@',
            object: '=',
            updateCallback: '&',
        },
        templateUrl: 'base/directives/editable_text.html',
        controller: EditableTextController,
        controllerAs: 'vm',
        transclude: true,
        bindToController: true,
    };
}

EditableTextController.$inject = ['HLUtils'];
function EditableTextController(HLUtils) {
    const vm = this;

    vm.updateViewModel = updateViewModel;

    activate();

    /////

    function activate() {
        // Setup the form name so we can block the element while saving data.
        vm.formName = vm.field.split('_').join('') + 'Form';
    }

    function updateViewModel(data) {
        return vm.updateCallback()(data, vm.field, vm.object);
    }
}
