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

EditableCheckboxController.$inject = ['HLResource'];
function EditableCheckboxController(HLResource) {
    var ec = this;

    ec.updateViewModel = updateViewModel;

    function updateViewModel() {
        var args = {
            id: ec.viewModel.id,
        };

        args[ec.field] = ec.viewModel[ec.field];

        return HLResource.patch(ec.type, args).$promise;
    }
}
