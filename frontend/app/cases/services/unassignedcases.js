angular.module('app.cases.services').factory('UnassignedTeamCases', UnassignedTeamCases);

UnassignedTeamCases.$inject = ['$resource'];
function UnassignedTeamCases ($resource) {
    return $resource('/api/cases/teams/:teamId/?is_assigned=False&is_archived=false&is_deleted=False')
}
