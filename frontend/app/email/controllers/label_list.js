angular.module('app.email').controller('LabelListController', LabelListController);

LabelListController.$inject = ['$filter', '$interval', '$scope', '$state', '$timeout', 'EmailAccount', 'HLUtils',
    'LocalStorage', 'primaryEmailAccountId'];
function LabelListController($filter, $interval, $scope, $state, $timeout, EmailAccount, HLUtils,
    LocalStorage, primaryEmailAccountId) {
    const vm = this;
    const storage = new LocalStorage('labelList');

    vm.labelSettings = storage.get('labelSettings', {});
    vm.accountList = [];
    vm.primaryEmailAccountId = primaryEmailAccountId;
    vm.labelCount = 0;
    vm.syncInProgress = false;

    vm.hasUnreadLabel = hasUnreadLabel;
    vm.unreadCountForLabel = unreadCountForLabel;
    vm.clickAccountHeader = clickAccountHeader;
    vm.toggleLabel = toggleLabel;

    activate();

    //////////

    function activate() {
        $timeout(() => {
            _startIntervalAccountInfo();
        }, 100);
    }

    function clickAccountHeader(account) {
        if (!account) {
            $state.go('base.email.list', {labelId: 'INBOX'});
        } else {
            $state.go('base.email.accountList', {labelId: 'INBOX', accountId: account.id});
        }
    }

    function _startIntervalAccountInfo() {
        _getAccountInfo();
        let stopGetAccountInfo = $interval(_getAccountInfo, 60000);

        // Stop fetching when out of scope.
        $scope.$on('$destroy', () => {
            // Make sure that the interval is destroyed too.
            if (stopGetAccountInfo) {
                $interval.cancel(stopGetAccountInfo);
                stopGetAccountInfo = null;
            }
        });
    }

    function _getParentLabelName(label) {
        let name = '';

        if (label.parent) {
            name = _getParentLabelName(label.parent);
        }

        name += `${label.name}/`;

        return name;
    }

    function _getParent(parentLabel, label) {
        const parentLabelName = _getParentLabelName(parentLabel);

        let parent;

        if (label.name.includes(parentLabelName)) {
            // We've reached the final parent and it seems the label is a child.
            parent = parentLabel;
            label.name = label.name.replace(parentLabelName, '');
        } else if (parentLabel.parent) {
            // The given parentLabel doesn't seem to be the label's parent.
            // So recursively check if the given parent's parent is the label's parent.
            parent = _getParent(parentLabel.parent, label);
        }

        if (parent) {
            label.parent = parent;
        }

        return parent;
    }

    // Fetch the EmailAccounts & associated labels.
    function _getAccountInfo() {
        EmailAccount.mine(results => {
            // Sort accounts on ID.
            const orderedResults = $filter('orderBy')(results.results, 'id');
            const accountList = [];

            // Make sure primary account is set first.
            orderedResults.forEach(account => {
                if (account.is_active) {
                    if (account.id !== vm.primaryEmailAccountId) {
                        accountList.push(account);
                    } else {
                        accountList.unshift(account);
                    }
                }
            });

            const labelCount = {};
            vm.accountList = accountList;

            // Check for unread email count.
            vm.accountList.forEach(account => {
                // Sort the labels by name.
                account.labels = account.labels.sort((a, b) => a.name.localeCompare(b.name));

                const labelList = [];
                let previousLabel = null;

                if (!account.color) {
                    account.color = HLUtils.getColorCode(account.email_address);
                }

                account.labels.forEach((label, index) => {
                    label.children = [];

                    if (vm.labelSettings.hasOwnProperty(label.id)) {
                        // Get stored settings for the label.
                        label.collapsed = vm.labelSettings[label.id];
                    }

                    if (!label.parent) {
                        // Initial indentation level.
                        label.level = 0;
                    }

                    let addToList = true;

                    if (previousLabel) {
                        const parent = _getParent(previousLabel, label);

                        if (parent) {
                            // Increase indentation level.
                            label.level = parent.level + 1;
                            parent.children.push(label);
                            // It's a child, so don't render it as part of the list,
                            // but part of the parent.
                            addToList = false;
                        }
                    }

                    previousLabel = label;

                    if (addToList) {
                        labelList.push(label);
                    }

                    if (label.label_type === 0) {
                        if (labelCount.hasOwnProperty(label.label_id)) {
                            labelCount[label.label_id] += parseInt(label.unread);
                        } else {
                            labelCount[label.label_id] = parseInt(label.unread);
                        }
                    }
                });

                account.labels = labelList;
            });

            vm.labelCount = labelCount;

            let progress = false;

            // Check if there is still one account doing a full sync to set the global sync status.
            for (let i in vm.accountList) {
                if (vm.accountList[i].is_syncing) {
                    progress = true;
                    break;
                }
            }
            vm.syncInProgress = progress;
        });
    }

    function unreadCountForLabel(account, labelId) {
        let count = 0;

        angular.forEach(account.labels, label => {
            if (label.label_id === labelId) {
                count = label.unread;
                return;
            }
        });

        return count;
    }

    function hasUnreadLabel(account, labelId) {
        // return unreadCountForLabel(account, labelId) > 0;
        return false;
    }

    function toggleLabel(label) {
        label.collapsed = !label.collapsed;

        vm.labelSettings[label.id] = label.collapsed;

        storage.put('labelSettings', vm.labelSettings);
    }
}
