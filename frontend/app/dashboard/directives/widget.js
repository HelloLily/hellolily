angular.module('app.dashboard.directives').directive('dashboardWidget', dashboardWidget);

function dashboardWidget() {
    return {
        restrict: 'E',
        scope: {
            widgetName: '='
        },
        templateUrl: 'dashboard/directives/widget.html',
        controller: DashboardWidgetController,
        controllerAs: 'vm',
        bindToController: true,
        transclude: true
    }
}

DashboardWidgetController.$inject = ['Cookie', '$scope'];
function DashboardWidgetController(Cookie, $scope) {
    var vm = this;
    var cookie = Cookie('widgetInfo');
    var widgetStatus = {
        hidden: 0,
        visible: 1,
        collapsed: 2
    };

    vm.cookieName = _getWidgetCookieName();

    vm.toggleCollapse = toggleCollapse;
    vm.removeWidget = removeWidget;

    activate();

    ////////////

    function activate() {
        // Get visibility status of the widget
        var widgetInfo = cookie.getObjectValue(vm.cookieName, {});
        var currentWidgetStatus = widgetInfo.status;

        if (typeof currentWidgetStatus === 'undefined') {
            // No cookie value yet, so set status to visible
            widgetInfo.status = widgetStatus.visible;
            widgetInfo.name = vm.widgetName;
        }

        vm.widgetInfo = widgetInfo;

        _updateWidgetCookie();

        _watchWidgetVisibility();
    }

    function _getWidgetCookieName() {
        // Strip all whitespace and make the name lowercase
        return vm.widgetName.replace(/\s+/g, '').toLowerCase();
    }

    function _watchWidgetVisibility () {
        // Check the status of a widget for changes and update the cookie
        $scope.$watch('vm.widgetInfo.status', function() {
            _updateWidgetCookie();
        });
    }

    /**
     * Sets the widget info cookie.
     * The cookie contains the name of the widget (used for settings)
     * and visibility status of the widget.
     */
    function _updateWidgetCookie() {
        cookie.putObjectValue(vm.cookieName, vm.widgetInfo);
    }

    function toggleCollapse() {
        if (vm.widgetInfo.status == 1) {
            vm.widgetInfo.status = widgetStatus.collapsed;
        }
        else {
            vm.widgetInfo.status = widgetStatus.visible;
        }
    }

    function removeWidget() {
        vm.widgetInfo.status = widgetStatus.hidden;
    }
}
