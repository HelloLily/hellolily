angular.module('app.timelogs.services').factory('TimeLog', TimeLog);

TimeLog.$inject = ['$resource', 'HLResource'];
function TimeLog($resource, HLResource) {
    const _timelog = $resource(
        '/api/timelogs/:id/',
        null,
        {
            query: {
                method: 'GET',
                params: {
                    model: '@model',
                    id: '@id',
                },
            },
            update: {
                method: 'PATCH',
                params: {
                    id: '@id',
                },
            },
            patch: {
                method: 'PATCH',
                params: {
                    id: '@id',
                },
            },
            getForObject: {
                url: '/api/:model/:id/timelogs',
                params: {
                    id: '@id',
                    model: '@model',
                },
                transformResponse: data => {
                    const jsonData = angular.fromJson(data);

                    if (jsonData && jsonData.objects && jsonData.objects.length > 0) {
                        jsonData.objects.forEach(timeLog => {
                            timeLog.activityType = 'timelog';
                        });
                    }

                    return jsonData;
                },
            },
        }
    );

    _timelog.updateModel = updateModel;

    /////////

    function updateModel(data, field, timelogObject) {
        const args = HLResource.createArgs(data, field, timelogObject);

        const patchPromise = HLResource.patch('TimeLog', args).$promise;

        return patchPromise;
    }

    return _timelog;
}
