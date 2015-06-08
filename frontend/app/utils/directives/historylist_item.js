angular.module('app.utils.directives').directive('historyListItem', HistoryListItemDirective);

HistoryListItemDirective.$inject = ['$compile', '$http', '$templateCache'];
function HistoryListItemDirective($compile, $http, $templateCache) {
    return {
        restrict: 'E',
        scope: {
            item:'=',
            history:'='
        },
        link: function(scope, element, attrs) {
            var getTemplate = function(historyType) {
                var templateLoader,
                    baseUrl = 'utils/directives/history_list_',
                    templateMap = {
                        case: 'case.html',
                        deal: 'deal.html',
                        email: 'email.html',
                        note: 'note.html'
                    };

                var templateUrl = baseUrl + templateMap[historyType];
                templateLoader = $http.get(templateUrl, {cache: $templateCache});

                return templateLoader;
            };
            getTemplate(scope.item.historyType).success(function(html) {
                element.replaceWith($compile(html)(scope));
            }).then(function () {
                element.replaceWith($compile(element.html())(scope));
            });
        }
    };
}
