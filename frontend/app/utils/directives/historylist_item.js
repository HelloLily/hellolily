angular.module('app.utils.directives').directive('historyListItem', HistoryListItemDirective);

HistoryListItemDirective.$inject = ['$compile', '$http', '$templateCache'];
function HistoryListItemDirective($compile, $http, $templateCache) {
    return {
        restrict: 'E',
        scope: {
            item: '=',
            history: '=',
            object: '=',
            deleteCallback: '&?',
            updateCallback: '&?',
        },
        link: function(scope, element, attrs) {
            var getTemplate = function(historyType) {
                var templateLoader;
                var baseUrl = 'utils/directives/history_list_';
                var templateMap = {
                    case: 'case.html',
                    deal: 'deal.html',
                    email: 'email.html',
                    note: 'note.html',
                };

                var templateUrl = baseUrl + templateMap[historyType];
                templateLoader = $http.get(templateUrl, {cache: $templateCache});

                return templateLoader;
            };
            getTemplate(scope.vm.item.historyType).success(function(html) {
                element.replaceWith($compile(html)(scope));
            }).then(function() {
                element.replaceWith($compile(element.html())(scope));
            });
        },
        controller: HistoryListItemController,
        bindToController: true,
        controllerAs: 'vm',
    };
}

HistoryListItemController.$inject = ['$state'];
function HistoryListItemController($state) {
    var vm = this;

    vm.replyOnEmail = replyOnEmail;

    /////

    function replyOnEmail() {
        // Check if the emailaccount belongs to the current contact or account.
        angular.forEach(vm.object.email_addresses, function(emailAddress) {
            if (emailAddress.email_address === vm.item.sender_email && emailAddress.status === 0) {
                // Is status is inactive, try to find other email address.
                _replyToGoodEmailAddress();
            }
        });

        function _replyToGoodEmailAddress() {
            // Try to find primary.
            angular.forEach(vm.object.email_addresses, function(emailAddress) {
                if (emailAddress.status === 2) {
                    $state.go('base.email.replyOtherEmail', {id: vm.item.id, email: emailAddress.email_address});
                }
            });

            // Other will do as alternative.
            angular.forEach(vm.object.email_addresses, function(emailAddress) {
                if (emailAddress.status === 1) {
                    $state.go('base.email.replyOtherEmail', {id: vm.item.id, email: emailAddress.email_address});
                }
            });
        }

        $state.go('base.email.reply', {id: vm.item.id});
    }
}
