angular.module('app.email.services').factory('EmailDetail', EmailDetail);

EmailDetail.$inject = ['$resource'];
function EmailDetail($resource) {
    // TODO: Merge with emailmessage.js search.
    var _emailDetail = $resource(
        '',
        {  // Defaults for parameters.
            size: 100,
            sort: '-sent_date',
        },
        {
            search: {
                url: 'api/messaging/email/search/?size=:size&sort=:sort',
                isArray: true,
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);
                    var objects = [];
                    if (jsonData && jsonData.hits && jsonData.hits.length > 0) {
                        jsonData.hits.forEach(function(obj) {
                            var emailDetail = $.extend(obj, {
                                activityType: 'email',
                                color: 'green',
                                date: obj.sent_date,
                                right: false,
                            });
                            objects.push(emailDetail);
                        });
                    }

                    return objects;
                },
            },
        }
    );
    return _emailDetail;
}
