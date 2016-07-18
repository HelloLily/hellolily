angular.module('app.directives').directive('editableTextarea', editableTextarea);

function editableTextarea() {
    return {
        restrict: 'E',
        scope: {
            viewModel: '=',
            field: '@',
            object: '=',
        },
        templateUrl: 'base/directives/editable_textarea.html',
        controller: EditableTextAreaController,
        controllerAs: 'vm',
        transclude: true,
        bindToController: true,
        link: function(scope, element, attrs) {
            // Bind click event to the current directive.
            element.on('click', '.hl-edit-icon', function() {
                scope.textAreaForm.$show();
            });
        },
    };
}

EditableTextAreaController.$inject = ['$timeout', 'HLUtils'];
function EditableTextAreaController($timeout, HLUtils) {
    var vm = this;

    vm.updateViewModel = updateViewModel;
    vm.decodeText = decodeText;

    activate();

    /////

    function activate() {
        vm.selectModel = vm.object[vm.field];
    }

    function decodeText() {
        // Convert the HTML entities to human readable characters.
        vm.selectModel = HLUtils.decodeHtmlEntities(vm.selectModel);
    }

    function updateViewModel($data) {
        var args = {
            id: vm.object.id,
        };

        args[vm.field] = $data;

        return vm.viewModel.updateModel(args).then(function(data) {
            // Set the encoded value so it get's properly displayed in the frontend.
            $timeout(function() {
                // Just setting the value doesn't update the values model properly.
                // So use $timeout so it gets applied in the next digest cycle.
                vm.object[vm.field] = data[vm.field];
            });
        });
    }
}
