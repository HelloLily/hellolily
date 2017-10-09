angular.module('app.dashboard.directives').directive('widget', widget);

function widget() {
    return {
        restrict: 'E',
        scope: {
            widgetName: '=',
            widgetCloseable: '=',
            widgetClass: '=',
            widgetScrollable: '=',
            widgetDynamicHeight: '=',
            widgetExpandable: '<',
        },
        templateUrl: 'base/directives/widget.html',
        controller: Widget,
        controllerAs: 'vm',
        bindToController: true,
        transclude: {
            widgetHeader: 'widgetHeader',
            widgetFilters: '?widgetFilters',
            widgetBody: 'widgetBody',
        },
    };
}

Widget.$inject = ['$scope', '$state', '$timeout', 'LocalStorage'];
function Widget($scope, $state, $timeout, LocalStorage) {
    const vm = this;
    const storage = new LocalStorage($state.current.name + 'widgetInfo');
    const widgetStatus = {
        hidden: 0,
        visible: 1,
        collapsed: 2,
        expanded: 3,
    };

    vm.storageName = _getWidgetStorageName();

    vm.toggleCollapse = toggleCollapse;
    vm.removeWidget = removeWidget;
    vm.heightToggle = heightToggle;

    activate();

    ////////////

    function activate() {
        // Get visibility status of the widget.
        const widgetInfo = storage.getObjectValue(vm.storageName, {});

        $timeout(() => {
            if (typeof widgetInfo === 'object' && !Object.keys(widgetInfo).length) {
                // No locally stored value, so set status to visible.
                widgetInfo.status = widgetStatus.visible;
                widgetInfo.name = vm.widgetName;
            }

            if (!widgetInfo.widgetClass) {
                widgetInfo.widgetClass = vm.widgetClass;
            }

            vm.widgetInfo = widgetInfo;

            _updateWidgetStorage();
            _watchWidgetVisibility();
        }, 100);
    }

    function _getWidgetStorageName() {
        // Strip all whitespace and make the name lowercase.
        return vm.widgetName.replace(/\s+/g, '').toLowerCase();
    }

    function _watchWidgetVisibility() {
        // Check the status of a widget for changes and update the locally stored value.
        $scope.$watchGroup([
            'vm.widgetInfo.status',
            'vm.widgetInfo.expandHeight',
        ], () => {
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
        const halfWidth = 'col-md-6';
        const fullWidth = 'col-md-12';

        if (vm.widgetInfo.status === widgetStatus.visible) {
            // Check if the fade is initially set to prevent it from showing up
            // when the widget isn't scrollable.
            if ($scope.vm.showFade) {
                $scope.vm.showFade = false;
            }

            vm.widgetInfo.status = widgetStatus.collapsed;

            if (vm.widgetExpandable) {
                vm.widgetInfo.widgetClass = halfWidth;
            }
        } else if (vm.widgetInfo.status === widgetStatus.expanded) {
            // Check if the fade is initially set to prevent it from showing up
            // when the widget isn't scrollable.
            if ($scope.vm.showFade) {
                $scope.vm.showFade = false;
            }

            vm.widgetInfo.status = widgetStatus.visible;

            if (vm.widgetExpandable) {
                vm.widgetInfo.widgetClass = halfWidth;
            }
        } else {
            if (vm.widgetExpandable) {
                vm.widgetInfo.status = widgetStatus.expanded;
                vm.widgetInfo.widgetClass = fullWidth;
            } else {
                vm.widgetInfo.status = widgetStatus.visible;
            }

            if ($scope.vm.showFade === false) {
                $scope.vm.showFade = true;
            }
        }
    }

    function heightToggle() {
        vm.widgetInfo.expandHeight = !vm.widgetInfo.expandHeight;
    }

    function removeWidget() {
        vm.widgetInfo.status = widgetStatus.hidden;
    }
}
