angular.module('app.dashboard.directives').directive('dashboardWidget', dashboardWidget);

function dashboardWidget() {
    return {
        restrict: 'E',
        scope: {
            widgetName: '=',
            widgetCloseable: '=',
            widgetClass: '=',
            widgetScrollable: '=',
            widgetDynamicHeight: '=',
        },
        templateUrl: 'dashboard/directives/widget.html',
        controller: DashboardWidgetController,
        controllerAs: 'vm',
        bindToController: true,
        transclude: true,
    };
}

DashboardWidgetController.$inject = ['LocalStorage', '$scope'];
function DashboardWidgetController(LocalStorage, $scope) {
    var vm = this;
    var storage = LocalStorage('widgetInfo');
    var widgetStatus = {
        hidden: 0,
        visible: 1,
        collapsed: 2,
    };

    vm.storageName = _getWidgetStorageName();
    vm.height = 250;

    vm.toggleCollapse = toggleCollapse;
    vm.removeWidget = removeWidget;

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

        if (vm.widgetDynamicHeight) {
            vm.height = 'auto';
        }
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
        if (vm.widgetInfo.status === 1) {
            vm.widgetInfo.status = widgetStatus.collapsed;
        } else {
            vm.widgetInfo.status = widgetStatus.visible;
        }
    }

    function removeWidget() {
        vm.widgetInfo.status = widgetStatus.hidden;
    }
}
