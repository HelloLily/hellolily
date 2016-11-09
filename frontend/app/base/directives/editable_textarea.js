angular.module('app.directives').directive('editableTextarea', editableTextarea);

function editableTextarea() {
    return {
        restrict: 'E',
        scope: {
            viewModel: '=',
            field: '@',
            object: '=',
            extraClass: '@',
        },
        templateUrl: 'base/directives/editable_textarea.html',
        controller: EditableTextAreaController,
        controllerAs: 'vm',
        transclude: true,
        bindToController: true,
    };
}

EditableTextAreaController.$inject = ['$injector', '$timeout', 'HLUtils'];
function EditableTextAreaController($injector, $timeout, HLUtils) {
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
        if (vm.selectModel) {
            vm.selectModel = HLUtils.decodeHtmlEntities(vm.selectModel);
        }
    }

    function updateViewModel($data) {
        var patchPromise;
        var modelName;
        var args = {
            id: vm.object.id,
        };

        args[vm.field] = $data;

        if (vm.object.historyType) {
            modelName = vm.object.historyType.charAt(0).toUpperCase() + vm.object.historyType.slice(1);

            patchPromise = $injector.get(modelName).updateModel(args);
        } else {
            patchPromise = vm.viewModel.updateModel(args);
        }

        return patchPromise.then(function(data) {
            // Set the encoded value so it get's properly displayed in the frontend.
            $timeout(function() {
                // Just setting the value doesn't update the values model properly.
                // So use $timeout so it gets applied in the next digest cycle.
                vm.object[vm.field] = data[vm.field];
            });
        });
    }
}
