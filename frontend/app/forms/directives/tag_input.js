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

TagInputController.$inject = ['Tag'];
function TagInputController(Tag) {
    var vm = this;

    vm.tagChoices = [];

    vm.refreshTags = refreshTags;
    vm.addTagChoice = addTagChoice;

    function refreshTags(query) {
        if (query.length >= 1) {
            var exclude = '';

            // Exclude tags already selected.
            angular.forEach(vm.object.tags, function(tag) {
                exclude += ' AND NOT name:' + tag.name;
            });

            Tag.search({query: query + exclude}, function(response) {
                vm.tagChoices = response;
            });
        } else {
            vm.tagChoices = Tag.query({filterquery: 'name:* AND object_id:' + vm.object.id, size: 50});
        }
    }

    function addTagChoice(tag) {
        return {
            name: tag,
        };
    }
}
