angular.module('app.directives').directive('editableTags', editableTags);

function editableTags() {
    return {
        restrict: 'E',
        scope: {
            viewModel: '=',
            type: '@',
        },
        templateUrl: 'base/directives/editable_tags.html',
        controller: EditableTagsController,
        controllerAs: 'vm',
        transclude: true,
        bindToController: true,
    };
}

EditableTagsController.$inject = ['$timeout', 'HLSearch', 'HLUtils'];
function EditableTagsController($timeout, HLSearch, HLUtils) {
    var vm = this;

    vm.refreshTags = refreshTags;
    vm.updateViewModel = updateViewModel;
    vm.addTagChoice = addTagChoice;

    activate();

    /////

    function activate() {
        vm.object = vm.viewModel[vm.type.toLowerCase()];
    }

    function refreshTags(query) {
        var searchPromise = HLSearch.refreshTags(query, vm.object.tags);

        if (searchPromise) {
            searchPromise.$promise.then(function(data) {
                vm.choices = data.objects;
            });
        }
    }

    function updateViewModel($data) {
        var tagIds = [];
        var removedTags = [];

        var args = {
            id: vm.object.id,
        };

        var form = '[name="vm.tagForm"]';

        HLUtils.blockUI(form, true);

        for (let tag of $data.filter(x => 'id' in x)) {
            tagIds.push(tag.id);
        }

        removedTags = vm.object.tags.filter(tag => tagIds.indexOf(tag.id) === -1);

        for (let tag of removedTags) {
            tag.is_deleted = true;
        }

        args.tags = $data.concat(removedTags);

        return vm.viewModel.updateModel(args).then(function(response) {
            HLUtils.unblockUI(form);
            vm.tagForm.$hide();

            // Just setting the value doesn't update the values model properly.
            // So use $timeout so it gets applied in the next digest cycle.
            $timeout(function() {
                vm.viewModel[vm.type.toLowerCase()].tags = response.tags;
            });
        });
    }

    function addTagChoice(tag) {
        return {
            name: tag,
        };
    }
}
