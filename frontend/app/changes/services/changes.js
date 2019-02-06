angular.module('app.changes').factory('Change', Change);

Change.$inject = ['$resource'];
function Change($resource) {
    const _change = $resource(
        '/api/:model/:id/changes/',
        null,
        {
            query: {
                method: 'GET',
                params: {
                    model: '@model',
                    id: '@id',
                },
                transformResponse: data => {
                    const jsonData = angular.fromJson(data);
                    const results = [];

                    if (jsonData && jsonData.results && jsonData.results.length > 0) {
                        jsonData.results.map(change => {
                            if (change.action !== 'post') {
                                change.activityType = 'change';
                                change.date = change.created;

                                results.push(change);
                            }
                        });
                    }

                    return {results};
                },
                isArray: false,
            },
        });

    return _change;
}
