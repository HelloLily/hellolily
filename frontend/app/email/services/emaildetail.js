angular.module('app.email.services').factory('EmailDetail', EmailDetail);

EmailDetail.$inject = ['$resource'];
function EmailDetail($resource) {
    var _emailDetail = $resource(
        '',
        {  // Defaults for parameters.
            size: 100,
        },
        {
            search: {
                url: '/search/search/?type=email_emailmessage&size=:size&sort=-sent_date&filterquery=:filterquery&account_related=:account_related',
                isArray: true,
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);
                    var objects = [];
                    if (jsonData && jsonData.hits && jsonData.hits.length > 0) {
                        jsonData.hits.forEach(function(obj) {
                            var emailDetail = $.extend(obj, {
                                historyType: 'email',
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
