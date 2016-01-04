angular.module('app.directives').directive('listWidget', ListWidget);

function ListWidget() {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            title: '@',
            module: '=',
            list: '=',
            height: '=',
            addLink: '@',
            collapsableItems: '=',
            account: '=',
        },
        templateUrl: function(elem, attrs) {
            var templateUrl = '';

            if (attrs.module) {
                // Some custom title is given, so use the given module name.
                templateUrl = attrs.module + '/directives/list_widget.html';
            } else {
                templateUrl = attrs.title.toLowerCase() + '/directives/list_widget.html';
            }

            return templateUrl;
        },
        controller: ListWidgetController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

ListWidgetController.$inject = [];
function ListWidgetController() {
    var vm = this;

    if (vm.collapsableItems) {
        // Certain list widget have collapsable cells, so set the default state to collapsed.
        angular.forEach(vm.list, function(item) {
            item.collapsed = true;
        });
    }
}

