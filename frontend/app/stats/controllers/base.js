angular.module('app.stats').config(statsConfig);

statsConfig.$inject = ['$stateProvider'];
function statsConfig($stateProvider) {
    $stateProvider.state('base.stats', {
        url: '/stats',
        views: {
            '@': {
                templateUrl: 'stats/controllers/base.html',
                controller: StatsBaseController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'test',
        },
    });
}

angular.module('app.stats').controller('StatsBaseController', StatsBaseController);

StatsBaseController.$inject = ['Settings', 'Stats'];
function StatsBaseController(Settings, Stats) {
    var vm = this;
    vm.totalCasesLastWeek = 0;
    vm.perTypeCountCases = {};
    vm.countWithTagsCases = 0;
    vm.countWithoutTagsCases = 0;
    vm.topTagsCases = {};

    Settings.page.setAllTitles('custom', 'Stats');

    activate();

    ////

    function activate() {
        _getTotalCountCases();
        _getPerTypeCountCases();
        _getCountWithTagsLastWeekCases();
        _getCountPerTypeCases();
        _getTopTagsCases();

        _getDealsUnsentFeedback();
        _getDealsUrgentFollowUp();
        _getDealsWon();
        _getDealsLost();
        _getDealsAmountRecurring();
    }

    function _getTotalCountCases() {
        Stats.query({
            'appname': 'cases',
            'endpoint': 'total',
            'groupid': 1,
        }, function(data) {
            vm.totalCasesLastWeek = data[0].count;
            vm.countWithoutTagsCases = vm.totalCasesLastWeek - vm.countWithTagsCases;
        });
    }

    function _getPerTypeCountCases() {
        Stats.query({
            'appname': 'cases',
            'endpoint': 'grouped',
            'groupid': 1,
        }, function(data) {
            vm.perTypeCountCases = data;
        });
    }

    function _getCountWithTagsLastWeekCases() {
        Stats.query({
            'appname': 'cases',
            'endpoint': 'withtags',
            'groupid': 1,
        }, function(data) {
            vm.countWithTagsCases = data[0].count;
            vm.countWithoutTagsCases = vm.totalCasesLastWeek - vm.countWithTagsCases;
        });
    }

    function _getCountPerTypeCases() {
        Stats.query({
            'appname': 'cases',
            'endpoint': 'countperstatus',
            groupid: 1,
        }, function(data) {
            vm.countPerStatus = data;
        });
    }

    function _getTopTagsCases() {
        Stats.query({
            'appname': 'cases',
            'endpoint': 'toptags',
            'groupid': 1,
        }, function(data) {
            vm.topTagCases = data;
        });
    }

    function _getDealsUnsentFeedback() {
        Stats.query({
            'appname': 'deals',
            'endpoint': 'unsentfeedback',
        }, function(data) {
            vm.dealsUnsentFeedback = data;
        });
    }

    function _getDealsUrgentFollowUp() {
        Stats.query({
            'appname': 'deals',
            'endpoint': 'urgentfollowup',
        }, function(data) {
            vm.dealsUrgentFollowUp = data;
        });
    }

    function _getDealsWon() {
        Stats.query({
            'appname': 'deals',
            'endpoint': 'won',
        }, function(data) {
            vm.dealsWon = data;
        });
    }

    function _getDealsLost() {
        Stats.query({
            'appname': 'deals',
            'endpoint': 'lost',
        }, function(data) {
            vm.dealsLost = data;
        });
    }

    function _getDealsAmountRecurring() {
        Stats.query({
            'appname': 'deals',
            'endpoint': 'amountrecurring',
        }, function(data) {
            vm.dealsAmountRecurring = data;
        });
    }
}
