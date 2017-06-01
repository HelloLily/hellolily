var md = require('markdown-it')();

md.renderer.rules.blockquote_open = (tokens, index) => {
    return '<blockquote class="blockquote">';
};

md.renderer.rules.table_open = (tokens, index) => {
    return '<table class="table">';
};

angular.module('app.directives').directive('editableTextarea', editableTextarea);

function editableTextarea() {
    return {
        restrict: 'E',
        scope: {
            viewModel: '=',
            field: '@',
            object: '=',
            extraClass: '@',
            modelName: '@?',
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
    vm.convertToHTML = convertToHTML;

    activate();

    /////

    function activate() {
        vm.selectModel = vm.object[vm.field];

        if (!vm.modelName && vm.object.activityType) {
            vm.modelName = vm.object.activityType.charAt(0).toUpperCase() + vm.object.activityType.slice(1);
        }
    }

    function convertToHTML() {
        // Convert Markdown to HTML.
        return vm.selectModel ? md.render(vm.selectModel) : '';
    }

    function updateViewModel($data) {
        const args = {
            id: vm.object.id,
            [vm.field]: $data,
        };

        let patchPromise;

        if (vm.object.activityType) {
            patchPromise = $injector.get(vm.modelName).updateModel(args);
        } else {
            patchPromise = vm.viewModel.updateModel(args);
        }

        return patchPromise.then(data => {
            // Set the encoded value so it get's properly displayed in the frontend.
            $timeout(() => {
                // Just setting the value doesn't update the values model properly.
                // So use $timeout so it gets applied in the next digest cycle.
                vm.object[vm.field] = data[vm.field];
            });
        });
    }
}
