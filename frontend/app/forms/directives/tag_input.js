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

TagInputController.$inject = ['$scope', '$filter', 'HLSearch'];
function TagInputController($scope, $filter, HLSearch) {
    var vm = this;

    vm.tagChoices = [];
    vm.firstSearch = true;

    vm.refreshTags = refreshTags;
    vm.addTagChoice = addTagChoice;
    vm.addTag = addTag;

    function refreshTags(query) {
        var searchPromise = HLSearch.refreshTags(query, vm.object.tags);

        if (searchPromise) {
            searchPromise.$promise.then(function(result) {
                if (vm.firstSearch) {
                    // Get the 5 last used tags.
                    vm.lastUsed = $filter('orderBy')(result.objects, '-last_used');
                    vm.mostUsed = result.objects;

                    vm.firstSearch = false;
                }

                vm.tagChoices = result.objects;
            });
        }
    }

    function addTagChoice(tag) {
        return {
            name: tag,
        };
    }

    function addTag(tag) {
        if (vm.object.tags.indexOf(tag) === -1) {
            vm.object.tags.push(tag);
        }
    }
}
