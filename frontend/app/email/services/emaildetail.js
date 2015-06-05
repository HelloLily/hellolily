angular.module('app.email.services').factory('EmailDetail', EmailDetail);

EmailDetail.$inject = ['$resource'];
function EmailDetail ($resource) {
    return $resource(
        '',
        {size:100},
        {
            query: {
                url: '/search/search/?type=email_emailmessage&size=:size&sort=-sent_date&filterquery=:filterquery&account_related=:account_related',
                isArray: true,
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    var objects = [];
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function(obj) {
                            obj = $.extend(obj, {historyType: 'email', color: 'green', date: obj.sent_date, right: false});
                            objects.push(obj)
                        });
                    }
                    return objects;
                }
            }
        }
    );
}
