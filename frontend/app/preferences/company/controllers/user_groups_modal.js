angular.module('app.preferences').controller('PreferencesUserGroupsModalController', PreferencesUserGroupsModalController);

PreferencesUserGroupsModalController.$inject = ['$uibModalInstance', 'HLForms', 'User', 'CacheFactory', 'user', 'groupList'];
function PreferencesUserGroupsModalController($uibModalInstance, HLForms, User, CacheFactory, user, groupList) {
    var vm = this;

    vm.user = user;
    vm.groupList = groupList.results;

    vm.ok = ok;
    vm.cancel = cancel;

    activate();

    /////

    function activate() {
        vm.groupList.forEach(function(group) {
            var selected = vm.user.lily_groups.filter(function(groupId) {
                return groupId === group.id;
            });
            group.selected = selected.length > 0;
        });
    }

    function ok(form) {
        var userObj = {};
        var selectedGroups = [];

        // Loop over emailAccountList to extract the selected accounts.
        vm.groupList.forEach(function(group) {
            if (group.selected) {
                selectedGroups.push(group.id);
            }
        });

        userObj.lily_groups = selectedGroups;

        // Use the User resource for updating the lily_groups attribute.
        User.patch({
            id: vm.user.id,
            is_active: 'All',
        }, userObj, function() {
            $uibModalInstance.close(vm.user);
            toastr.success('I\'ve updated the users\' groups for you!', 'Done');
        }, function(response) {
            HLForms.setErrors(form, response.data);
            toastr.error('Uh oh, there seems to be a problem', 'Oops!');
        });
    }

    // Let's not change anything.
    function cancel() {
        $uibModalInstance.dismiss('cancel');
    }
}
