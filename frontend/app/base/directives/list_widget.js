angular.module('app.directives').directive('listWidget', ListWidget);

function ListWidget() {
    return {
        restrict: 'E',
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

ListWidgetController.$inject = ['$filter', '$state', 'Settings'];
function ListWidgetController($filter, $state, Settings) {
    var vm = this;

    vm.settings = Settings;

    vm.googleAnalyticsEvent = googleAnalyticsEvent;

    activate();

    /////

    function activate() {
        if (vm.collapsableItems) {
            // Certain list widgets have collapsable cells, so set the default state to collapsed.
            if (!vm.list.hasOwnProperty('$promise')) {
                // Array was passed, so just pass the list.
                _setCollapsed(vm.list);
            } else {
                vm.list.$promise.then(function(response) {
                    // List hasn't fully loaded, so wait and pass the response.
                    _setCollapsed(response);
                });
            }
        }
    }

    // Google Analytics function to set labels to differentiate in Analytics
    // which widget the user used to add a case or deal.
    function googleAnalyticsEvent() {
        if ($state.current.name === 'base.contacts.detail' && vm.title === 'Cases') {
            ga('send', 'event', 'Case', 'Open', 'Contact Widget');
        }

        if ($state.current.name === 'base.accounts.detail' && vm.title === 'Cases') {
            ga('send', 'event', 'Case', 'Open', 'Account Widget');
        }

        if ($state.current.name === 'base.contacts.detail' && vm.title === 'Deals') {
            ga('send', 'event', 'Deal', 'Open', 'Contact Widget');
        }

        if ($state.current.name === 'base.accounts.detail' && vm.title === 'Deals') {
            ga('send', 'event', 'Deal', 'Open', 'Account Widget');
        }

        if ($state.current.name === 'base.accounts.detail' && vm.title !== 'Deals' && vm.title !== 'Cases') {
            ga('send', 'event', 'Contact', 'Open', 'Account Widget');
        }

        if ($state.current.name === 'base.contacts.detail' && vm.title !== 'Deals' && vm.title !== 'Cases') {
            ga('send', 'event', 'Contact', 'Open', 'Contact Widget');
        }
    }

    function _setCollapsed(items) {
        var list;
        var cases;
        var deals;
        var archivedCases;
        var archivedDeals;

        if (items.hasOwnProperty('objects')) {
            list = items.objects;
        } else {
            list = items;
        }

        angular.forEach(list, function(item) {
            item.collapsed = true;
        });

        // We want to apply a certain sorting for cases.
        if (vm.title === 'Cases') {
            // Separate non-archived cases and order by priority.
            cases = $filter('filter')(list, {is_archived: false});
            cases = $filter('orderBy')(cases, '-priority');

            // Separate archived cases and order by expiry date.
            archivedCases = $filter('filter')(list, {is_archived: true});
            archivedCases = $filter('orderBy')(archivedCases, '-expires');

            // Add archived cases to cases array.
            cases.push.apply(cases, archivedCases);

            list = cases;
        }

        // We want to apply a certain sorting for deals.
        if (vm.title === 'Deals') {
            // Separate non-archived deals.
            deals = $filter('filter')(list, {is_archived: false});

            // Separate archived deals.
            archivedDeals = $filter('filter')(list, {is_archived: true});

            // Add archived deals to deals array.
            deals.push.apply(deals, archivedDeals);

            list = deals;
        }

        vm.list = list;
    }
}
