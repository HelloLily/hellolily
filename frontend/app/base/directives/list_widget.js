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
            object: '=',
        },
        templateUrl: function(elem, attrs) {
            var templateUrl = '';

            if (attrs.module) {
                // Template url can't be determined from the given title. So use the module name.
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
        // Certain list widgets have collapsable cells, so set the default state to collapsed.
        angular.forEach(vm.list, function(item) {
            item.collapsed = true;
        });
    }
}

