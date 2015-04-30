(function() {
    'use strict';

    /**
     * Controller for the UnassignedCases dashboard widget(s), which shows
     * a widget per team for unassigned cases.
     */
    angular.module('app.dashboard.directives').directive('teams', teams);

    function teams () {
        return {
            templateUrl: 'dashboard/teams.html',
            controller: Teams,
            controllerAs: 'uc'
        }
    }

    Teams.$inject = ['UserTeams'];
    function Teams (UserTeams) {
        var vm = this;
        vm.teams = [];

        activate();

        /////

        function activate() {
            _getTeams();
        }

        function _getTeams() {
            UserTeams.query(function(teams) {
                vm.teams = teams;
            });
        }
    }
})();
