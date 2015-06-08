angular.module('app.deals.services').factory('DealStages', DealStages);

DealStages.$inject = ['$resource'];

function DealStages ($resource) {
    return $resource('/api/deals/stages');
}
