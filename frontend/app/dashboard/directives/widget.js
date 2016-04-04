angular.module('app.dashboard.directives').directive('dashboardWidget', dashboardWidget);

function dashboardWidget($timeout) {
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
        transclude: {
            widgetHeader: 'widgetHeader',
            widgetFilters: '?widgetFilters',
            widgetBody: 'widgetBody',
        },
        link: function(scope, element, attrs) {
            // Timeout function to wait for elements to fully load in DOM.
            // This function checks if the scrollheight is higher than 250px
            // to indicate that the widget is scrollable.
            $timeout(function() {
                var height = (scope.vm.widgetDynamicHeight ? 401 : 252);
                if(scope.vm.widgetScrollable === true){
                    var rawDomElement = element.parent().find('.widget-table')[0];
                    if (rawDomElement && rawDomElement.scrollHeight > height) {
                        if(!scope.vm.showFade){
                            scope.vm.showFade = true;
                        }
                    }
                }
            });
        },
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
    vm.hideScrollingIndicator = hideScrollingIndicator;
    vm.showScrollingIndicator = showScrollingIndicator;

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

    // Event triggered by ng-mouseenter to remove the scrolling indicator
    // when a user has his mouse in the widget.
    function hideScrollingIndicator() {
        if ($scope.vm.showFade) {
            $scope.vm.showFade = false;
        }
    }

    function showScrollingIndicator() {
        // Specifically check if the value is set to false, because the
        // false value only gets set after the removeFade function has been
        // triggered by an ng-mouseenter event on the element.
        // This prevents the showFade value becoming true on elements that
        // are not scrollable.
        if ($scope.vm.showFade === false) {
            $scope.vm.showFade = true;
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
            // Check if the fade is initially set to prevent it from showing up
            // when the widget isn't scrollable.
            if ($scope.vm.showFade) {
                $scope.vm.showFade = false;
            }
            vm.widgetInfo.status = widgetStatus.collapsed;
        } else {
            if($scope.vm.showFade === false){
                $scope.vm.showFade = true;
            }
            vm.widgetInfo.status = widgetStatus.visible;
        }
    }

    function removeWidget() {
        vm.widgetInfo.status = widgetStatus.hidden;
    }
}
