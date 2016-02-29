angular.module('app.directives').directive('editableCheckbox', editableCheckbox);

function editableCheckbox() {
    return {
        restrict: 'E',
        scope: {
            viewModel: '=',
            field: '@',
            type: '@',
        },
        templateUrl: 'base/directives/editable_checkbox.html',
        controller: EditableCheckboxController,
        controllerAs: 'ec',
        transclude: true,
        bindToController: true,
    };
}

EditableCheckboxController.$inject = [];
function EditableCheckboxController() {
    var ec = this;

    ec.object = ec.viewModel[ec.type.toLowerCase()];

    ec.updateViewModel = updateViewModel;

    function updateViewModel() {
        var args = {
            id: ec.object.id,
        };

        args[ec.field] = ec.object[ec.field];

        return ec.viewModel.updateModel(args);
    }
}
