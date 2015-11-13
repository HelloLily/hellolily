
angular.module('app.dashboard.directives').directive('feedback', feedbackDirective);

function feedbackDirective () {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/feedback.html',
        controller: FeedbackController,
        controllerAs: 'vm'
    }
}

FeedbackController.$inject = ['$scope', '$state', 'Account', 'Cookie', 'Deal', 'CaseDetail'];
function FeedbackController ($scope, $state, Account, Cookie, Deal, CaseDetail) {
    var cookie = Cookie('feedbackWidget');

    var vm = this;
    vm.table = {
        order: cookie.get('order', {
            ascending: true,
            column: 'closing_date'  // string: current sorted column
        }),
        items: []
    };

    vm.feedbackFormSentForDeal = feedbackFormSentForDeal;
    vm.openFeedbackForm = openFeedbackForm;

    activate();

    ///////////

    function activate () {
        _watchTable();
    }

    function _getFeedbackDeals () {
        var feedbackDeals = [];

        Deal.getFeedbackDeals(
            vm.table.order.column,
            vm.table.order.ascending
        ).then(function (dealList) {
            // vm.table.items = dealList;
            angular.forEach(dealList, function(deal) {
                var caseList = CaseDetail.query({filterquery: 'account:' + deal.account, archived: false});
            });

            vm.table.items = feedbackDeals;
        });
    }

    function feedbackFormSentForDeal (deal) {
        deal.feedbackFormSent().then(function() {
           vm.table.items.splice(vm.table.items.indexOf(deal), 1);
        });
    }

    function openFeedbackForm (deal) {
        Account.get({id: deal.account}, function(account) {
            var emailAddress = account.getEmailAddress();
            if (emailAddress) {
                $state.go('base.email.composeEmail', {email: emailAddress.email_address});
            } else {
                $state.go('base.email.compose');
            }
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.ascending', 'vm.table.order.column'], function() {
            _getFeedbackDeals();
            cookie.put('order', vm.table.order);
        })
    }
}
