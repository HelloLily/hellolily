angular.module('app.stats').config(statsConfig);

statsConfig.$inject = ['$stateProvider'];
function statsConfig ($stateProvider) {
    $stateProvider.state('base.stats', {
        url: '/stats',
        views: {
            '@': {
                templateUrl: 'stats/controllers/base.html',
                controller: StatsBaseController,
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: 'test'
        }
    });
}

angular.module('app.stats').controller('StatsBaseController', StatsBaseController);

StatsBaseController.$inject = ['$scope', 'Case'];
function StatsBaseController ($scope, Case) {
    var vm = this;
    vm.totalCasesLastWeek = 0;
    vm.perTypeCountCases = {};
    vm.countWithTagsCases = 0;
    vm.countWithoutTagsCases = 0;
    vm.topTagsCases = {};

    $scope.conf.pageTitleBig = 'Stats';
    $scope.conf.pageTitleSmall = 'All you can stat';

    activate();

    ////

    function activate () {
        _getTotalCountCases();
        _getPerTypeCountCases();
        _getCountWithTagsLastWeekCases();
        _getCountperTypeCases();
        _getTopTagsCases();
    }

    function _getTotalCountCases () {
        Case.getTotalCountLastWeek(1).then(function(data) {
            vm.totalCasesLastWeek = data[0].count;
            vm.countWithTagsCases = vm.totalCasesLastWeek - vm.countWithTagsCases;
        });
    }

    function _getPerTypeCountCases () {
        Case.getPerTypeCountLastWeek(1).then(function(data) {
            vm.perTypeCountCases = data;
        });
    }

    function _getCountWithTagsLastWeekCases () {
        Case.getCountWithTagsLastWeek(1).then(function(data) {
            vm.countWithTagsCases = data[0].count;
            vm.countWithoutTagsCases = vm.totalCasesLastWeek - vm.countWithTagsCases;
        });
    }

    function _getCountperTypeCases () {
        Case.getCountPerStatus(1).then(function(data) {
            vm.countPerStatus = data;
        });
    }

    function _getTopTagsCases () {
        Case.getTopTags(1).then(function(data) {
            vm.topTagsCases = data;
        });
    }

}
