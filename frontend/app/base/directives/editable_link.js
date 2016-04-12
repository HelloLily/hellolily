angular.module('app.directives').directive('editableLink', editableLink);

function editableLink() {
    return {
        restrict: 'E',
        scope: {
            viewModel: '=',
            type: '@',
            field: '@',
            object: '=?',
        },
        templateUrl: 'base/directives/editable_link.html',
        controller: EditableLinkController,
        controllerAs: 'el',
        transclude: true,
        bindToController: true,
        link: function(scope, element, attrs) {
            // Bind click event to the current directive.
            element.on('click', '.hl-edit-icon', function() {
                scope.linkForm.$show();
            });
        },
    };
}

EditableLinkController.$inject = [];
function EditableLinkController() {
    var el = this;

    el.updateViewModel = updateViewModel;

    activate();

    /////

    function activate() {
        if (!el.object) {
            el.object = el.viewModel[el.type.toLowerCase()];
        }
    }

    function updateViewModel($data) {
        var args = {
            id: el.object.id,
        };

        args[el.field] = $data;

        return el.viewModel.updateModel(args);
    }
}
