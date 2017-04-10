angular.module('app.dashboard.directives').directive('widget', simpleWidget);

function simpleWidget() {
    return {
        restrict: 'E',
        scope: {
            widgetName: '=',
            widgetCloseable: '=',
            widgetClass: '=',
            widgetScrollable: '=',
            widgetDynamicHeight: '=',
        },
        templateUrl: 'base/directives/widget.html',
        controller: SimpleWidget,
        controllerAs: 'vm',
        bindToController: true,
        transclude: {
            widgetHeader: 'widgetHeader',
            widgetFilters: '?widgetFilters',
            widgetBody: 'widgetBody',
        },
    };
}

SimpleWidget.$inject = ['$scope', '$state', 'LocalStorage'];
function SimpleWidget($scope, $state, LocalStorage) {
    var vm = this;
    var storage = new LocalStorage($state.current.name + 'widgetInfo');
    var widgetStatus = {
        hidden: 0,
        visible: 1,
        collapsed: 2,
        expanded: 3,
    };

    vm.storageName = _getWidgetStorageName();

    vm.toggleCollapse = toggleCollapse;
    vm.removeWidget = removeWidget;
    vm.expandToggle = expandToggle;

    activate();

    ////////////

    function activate() {
        // Get visibility status of the widget
        var widgetInfo = storage.getObjectValue(vm.storageName, {});

        if (typeof widgetInfo === 'object' && !Object.keys(widgetInfo).length) {
            // No locally stored value, so set status to visible
            widgetInfo.status = widgetStatus.visible;
            widgetInfo.name = vm.widgetName;
        }

        vm.widgetInfo = widgetInfo;

        _updateWidgetStorage();
        _watchWidgetVisibility();
    }

    function _getWidgetStorageName() {
        // Strip all whitespace and make the name lowercase
        return vm.widgetName.replace(/\s+/g, '').toLowerCase();
    }

    function _watchWidgetVisibility() {
        // Check the status of a widget for changes and update the locally stored value
        $scope.$watch('vm.widgetInfo.status', function() {
            _updateWidgetStorage();
        });
    }

    /**
     * Stores the widget info in local storage.
     * The widget info contains the name of the widget (used for settings)
     * and visibility status of the widget.
     */
    function _updateWidgetStorage() {
        storage.putObjectValue(vm.storageName, vm.widgetInfo);
    }

    function toggleCollapse() {
        if (vm.widgetInfo.status === widgetStatus.visible || vm.widgetInfo.status === widgetStatus.expanded) {
            // Check if the fade is initially set to prevent it from showing up
            // when the widget isn't scrollable.
            if ($scope.vm.showFade) {
                $scope.vm.showFade = false;
            }

            vm.widgetInfo.status = widgetStatus.collapsed;
        } else {
            if ($scope.vm.showFade === false) {
                $scope.vm.showFade = true;
            }

            vm.widgetInfo.status = widgetStatus.visible;
        }
    }

    function expandToggle() {
        if (vm.widgetInfo.status === widgetStatus.visible) {
            vm.widgetInfo.status = widgetStatus.expanded;
        } else {
            vm.widgetInfo.status = widgetStatus.visible;
        }
    }

    function removeWidget() {
        vm.widgetInfo.status = widgetStatus.hidden;
    }
}
