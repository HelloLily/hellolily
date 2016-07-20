angular.module('app.dashboard.directives').directive('teams', teamsDirective);

function teamsDirective() {
    return {
        templateUrl: 'dashboard/directives/teams.html',
        controller: TeamsController,
        controllerAs: 'vm',
    };
}

TeamsController.$inject = ['UserTeams'];
function TeamsController(UserTeams) {
    var vm = this;
    vm.teams = [];

    activate();

    /////

    function activate() {
        _getTeams();
    }

    function _getTeams() {
        UserTeams.mine(function(teams) {
            vm.teams = teams;
        });
    }
}
