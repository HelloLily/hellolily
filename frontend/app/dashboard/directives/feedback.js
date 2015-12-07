
angular.module('app.dashboard.directives').directive('feedback', feedbackDirective);

function feedbackDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/feedback.html',
        controller: FeedbackController,
        controllerAs: 'vm',
    };
}

FeedbackController.$inject = ['$scope', '$state', 'Account', 'LocalStorage', 'Deal', 'CaseDetail'];
function FeedbackController($scope, $state, Account, LocalStorage, Deal, CaseDetail) {
    var storage = LocalStorage('feedbackWidget');

    var vm = this;
    vm.table = {
        order: storage.get('order', {
            descending: true,
            column: 'next_step_date',  // string: current sorted column
        }),
        items: [],
    };

    vm.feedbackFormSentForDeal = feedbackFormSentForDeal;
    vm.openFeedbackForm = openFeedbackForm;

    activate();

    ///////////

    function activate() {
        _watchTable();
    }

    function _getFeedbackDeals() {
        var filterQuery = 'stage:2 AND feedback_form_sent:false AND assigned_to_id:' + currentUser.id;
        var dealPromise = Deal.getDeals('', 1, 20, vm.table.order.column, vm.table.order.descending, filterQuery);

        dealPromise.then(function(dealList) {
            angular.forEach(dealList, function(deal) {
                CaseDetail.query({filterquery: 'account:' + deal.account + ' AND archived:false'}).$promise.then(function(caseList) {
                    if (caseList.length > 0) {
                        deal.hasUnarchivedCases = true;
                    }
                });
            });

            vm.table.items = dealList;
        });
    }

    function feedbackFormSentForDeal(deal) {
        deal.feedbackFormSent().then(function() {
            vm.table.items.splice(vm.table.items.indexOf(deal), 1);
        });
    }

    function openFeedbackForm(deal) {
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
        $scope.$watchGroup(['vm.table.order.descending', 'vm.table.order.column'], function() {
            _getFeedbackDeals();
            storage.put('order', vm.table.order);
        });
    }
}
