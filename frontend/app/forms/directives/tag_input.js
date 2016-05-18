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
        var exclude = '';
        if (query.length >= 1) {
            // Exclude tags already selected.
            angular.forEach(vm.object.tags, function(tag) {
                exclude += ' AND NOT name_flat:' + tag.name;
            });

            vm.tagChoices = Tag.search({query: query + exclude});
        }
    }

    function addTagChoice(tag) {
        return {
            name: tag,
        };
    }
}
