angular.module('app.cases.services').factory('CaseStatuses', CaseStatuses);

CaseStatuses.$inject = ['$resource'];
function CaseStatuses ($resource) {
    return $resource('/api/cases/statuses');
}
