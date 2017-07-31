angular.module('app.changes').factory('Change', Change);

Change.$inject = ['$resource'];
function Change($resource) {
    var _change = $resource(
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
                    let jsonData = angular.fromJson(data);
                    let objects = [];

                    if (jsonData) {
                        if (jsonData.objects && jsonData.objects.length > 0) {
                            jsonData.objects.map(change => {
                                if (change.action !== 'post') {
                                    change.activityType = 'change';
                                    change.date = change.created;

                                    objects.push(change);
                                }
                            });
                        }
                    }

                    return {
                        objects: objects,
                    };
                },
            },
        });

    return _change;
}
