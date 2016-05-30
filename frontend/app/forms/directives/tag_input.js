angular.module('app.forms.directives').directive('tagInput', tagInput);

function tagInput() {
    return {
        restrict: 'E',
        scope: {
            object: '=',
        },
        templateUrl: 'forms/directives/tag_input.html',
        controller: TagInputController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

TagInputController.$inject = ['HLSearch'];
function TagInputController(HLSearch) {
    var vm = this;

    vm.tagChoices = [];

    vm.refreshTags = refreshTags;
    vm.addTagChoice = addTagChoice;

    function refreshTags(query) {
        var tagPromise = HLSearch.refreshTags(query, vm.object.tags);

        if (tagPromise) {
            tagPromise.$promise.then(function(result) {
                vm.tagChoices = result.objects;
            });
        }
    }

    function addTagChoice(tag) {
        return {
            name: tag,
        };
    }
}
