angular.module('app.integrations').factory('Moneybird', Moneybird);

Moneybird.$inject = ['$resource'];
function Moneybird($resource) {
    var _moneybird = $resource(
        '/api/integrations/moneybird/',
        null,
        {
            setupSync: {
                url: '/api/integrations/moneybird/import/',
                method: 'POST',
            },
            getEstimates: {
                url: '/api/integrations/moneybird/estimates/:contact/',
            },
        }
    );

    return _moneybird;
}
