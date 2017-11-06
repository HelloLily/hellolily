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
                    const objects = [];

                    if (jsonData && jsonData.objects && jsonData.objects.length > 0) {
                        jsonData.objects.map(change => {
                            if (change.action !== 'post') {
                                change.activityType = 'change';
                                change.date = change.created;

                                objects.push(change);
                            }
                        });
                    }

                    return {objects};
                },
            },
        });

    return _change;
}
