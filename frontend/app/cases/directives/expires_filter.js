angular.module('app.cases.directives').directive('caseExpiresFilter', caseExpiresFilter);

function caseExpiresFilter() {
    return {
        restrict: 'E',
        scope: {
            filterStore: '='
        },
        templateUrl: 'cases/directives/expires_filter.html',
        controller: CaseExpiresFilterWidgetController,
        controllerAs: 'vm',
        bindToController: true
    }
}

CaseExpiresFilterWidgetController.$inject = ['Cookie', '$scope'];
function CaseExpiresFilterWidgetController(Cookie, $scope) {
    var vm = this;
    var cookie = Cookie('case');

    // Get the stored value or set to 'All' if it doesn't exist
    vm.expiresFilter = cookie.get('expiresFilter', 0);

    activate();

    ////////////

    function activate() {
        _watchExpiresFilter();
    }

    function _watchExpiresFilter() {
        $scope.$watch('vm.expiresFilter', function () {
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
                    var tomorrow = moment().add(1, 'd').format('YYYY-MM-DD');
                    var week = moment().add(7, 'd').format('YYYY-MM-DD');
                    filter = 'expires: [' + tomorrow + ' TO ' + week + ']';
                    break;
            }

            cookie.put('expiresFilter', vm.expiresFilter);
            vm.filterStore = filter;
        });
    }
}
