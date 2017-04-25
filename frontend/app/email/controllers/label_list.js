angular.module('app.email').controller('LabelListController', LabelListController);

LabelListController.$inject = ['$filter', '$interval', '$scope', '$state', 'EmailAccount', 'primaryEmailAccountId'];
function LabelListController($filter, $interval, $scope, $state, EmailAccount, primaryEmailAccountId) {
    var vm = this;
    vm.accountList = [];
    vm.primaryEmailAccountId = primaryEmailAccountId;
    vm.labelCount = 0;
    vm.syncInProgress = false;

    vm.hasUnreadLabel = hasUnreadLabel;
    vm.unreadCountForLabel = unreadCountForLabel;
    vm.clickAccountHeader = clickAccountHeader;

    activate();

    //////////

    function activate() {
        _startIntervalAccountInfo();
    }

    function clickAccountHeader(account) {
        if (!account) {
            $state.go('base.email.list', {labelId: 'INBOX'});
        } else {
            $state.go('base.email.accountList', {labelId: 'INBOX', accountId: account.id});
        }
    }

    function _startIntervalAccountInfo() {
        var stopGetAccountInfo;

        _getAccountInfo();
        stopGetAccountInfo = $interval(_getAccountInfo, 60000);

        // Stop fetching when out of scope.
        $scope.$on('$destroy', function() {
            // Make sure that the interval is destroyed too.
            if (stopGetAccountInfo) {
                $interval.cancel(stopGetAccountInfo);
                stopGetAccountInfo = null;
            }
        });
    }

    // Fetch the EmailAccounts & associated labels.
    function _getAccountInfo() {
        EmailAccount.mine(function(results) {
            var i;
            var j;
            var label;
            var labelCount = {};
            // Sort accounts on id.
            var orderedResults = $filter('orderBy')(results, 'id');
            var progress = false;

            vm.accountList = [];
            // Make sure primary account is set first.
            angular.forEach(orderedResults, function(account) {
                if (account.id !== vm.primaryEmailAccountId) {
                    this.push(account);
                } else {
                    this.unshift(account);
                }
            }, vm.accountList);

            // Check for unread email count.
            for (i in vm.accountList) {
                for (j in vm.accountList[i].labels) {
                    label = vm.accountList[i].labels[j];

                    if (label.label_type === 0) {
                        if (labelCount.hasOwnProperty(label.label_id)) {
                            labelCount[label.label_id] += parseInt(label.unread);
                        } else {
                            labelCount[label.label_id] = parseInt(label.unread);
                        }
                    }
                }
            }
            vm.labelCount = labelCount;

            // Check if there is still one account doing a full sync to set the global sync status.
            for (i in vm.accountList) {
                if (vm.accountList[i].is_syncing) {
                    progress = true;
                    break;
                }
            }
            vm.syncInProgress = progress;
        });
    }

    function unreadCountForLabel(account, labelId) {
        var count = 0;
        angular.forEach(account.labels, function(label) {
            if (label.label_id === labelId) {
                count = label.unread;
                return;
            }
        });

        return count;
    }

    function hasUnreadLabel(account, labelId) {
        return unreadCountForLabel(account, labelId) > 0;
    }
}
