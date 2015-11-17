angular.module('app.cases.directives').directive('caseExpiresFilter', caseExpiresFilter);

function caseExpiresFilter() {
    return {
        restrict: 'E',
        scope: {
            filterStore: '=',
        },
        templateUrl: 'cases/directives/expires_filter.html',
        controller: CaseExpiresFilterWidgetController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

CaseExpiresFilterWidgetController.$inject = ['LocalStorage', '$scope'];
function CaseExpiresFilterWidgetController(LocalStorage, $scope) {
    var vm = this;
    var storage = LocalStorage('case');

    // Get the stored value or set to 'All' if it doesn't exist
    vm.expiresFilter = storage.get('expiresFilter', 0);

    activate();

    ////////////

    function activate() {
        _watchExpiresFilter();
    }

    function _watchExpiresFilter() {
        $scope.$watch('vm.expiresFilter', function() {
            var filter = '';

            switch (vm.expiresFilter) {
                case 0:
                    filter = '';
                    break;
                case 1:
                    var today = moment().format('YYYY-MM-DD');
                    filter = 'expires: ' + today;
                    break;
                case 2:
                    var tomorrow = moment().add(1, 'd').format('YYYY-MM-DD');
                    filter = 'expires: ' + tomorrow;
                    break;
                case 3:
                    var today = moment().format('YYYY-MM-DD');
                    var week = moment().add(6, 'd').format('YYYY-MM-DD');
                    filter = 'expires: [' + today + ' TO ' + week + ']';
                    break;
                case 4:
                    var today = moment().format('YYYY-MM-DD');
                    filter = 'expires:[* TO ' + moment().subtract(1, 'd').format('YYYY-MM-DD') + ']';
                    break;
            }

            storage.put('expiresFilter', vm.expiresFilter);
            vm.filterStore = filter;
        });
    }
}
