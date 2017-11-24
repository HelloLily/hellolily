angular.module('app.directives').directive('editableLink', editableLink);

function editableLink() {
    return {
        restrict: 'E',
        scope: {
            viewModel: '=',
            type: '@',
            field: '@',
            object: '=?',
            socialMediaName: '@?',
        },
        templateUrl: 'base/directives/editable_link.html',
        controller: EditableLinkController,
        controllerAs: 'el',
        transclude: true,
        bindToController: true,
    };
}

EditableLinkController.$inject = [];
function EditableLinkController() {
    const el = this;

    el.updateViewModel = updateViewModel;

    activate();

    /////

    function activate() {
        if (!el.object) {
            if (!el.socialMediaName) {
                el.object = el.viewModel[el.type.toLowerCase()];
            }
        }
    }

    function updateViewModel($data) {
        const args = {
            [el.field]: $data,
        };

        if (el.object) {
            args.id = el.object.id;
        }

        let patchPromise;

        if (el.socialMediaName) {
            if ($data) {
                args.name = el.socialMediaName;
            } else {
                args.is_deleted = true;
            }

            patchPromise = el.viewModel.updateModel(args, el.socialMediaName);
        } else {
            patchPromise = el.viewModel.updateModel(args).$promise;
        }

        return patchPromise;
    }
}
