angular.module('app.preferences').controller('EmailAccountShareModalController', EmailAccountShareModalController);

EmailAccountShareModalController.$inject = ['$uibModalInstance', 'EmailAccount', 'User', 'currentAccount'];
function EmailAccountShareModalController($uibModalInstance, EmailAccount, User, currentAccount) {
    var vm = this;
    vm.currentAccount = currentAccount;
    vm.ok = ok;
    vm.cancel = cancel;

    activate();

    ///////////////////

    function activate() {
        // Get all users to display in a list.
        User.query({}, function(data) {
            vm.users = [];
            // Check if user has the email account already shared.
            angular.forEach(data.results, function(user) {
                // Can't share with yourself, so don't include own user.
                if (user.id !== currentUser.id) {
                    if (vm.currentAccount.shared_with_users.indexOf(user.id) !== -1) {
                        user.sharedWith = true;
                    }

                    vm.users.push(user);
                }
            });
        });
    }

    function ok() {
        var sharedWithUsers = [];

        // Save updated account information.
        if (vm.currentAccount.public) {
            EmailAccount.update({id: vm.currentAccount.id}, vm.currentAccount, function() {
                $uibModalInstance.close();
            });
        } else {
            // Get ids of the users to share with.
            angular.forEach(vm.users, function(user) {
                if (user.sharedWith) {
                    sharedWithUsers.push(user.id);
                }
            });
            // Push ids to api.
            EmailAccount.shareWith({id: vm.currentAccount.id}, {shared_with_users: sharedWithUsers}, function() {
                $uibModalInstance.close();
            });
        }
    }

    // Let's not change anything.
    function cancel() {
        $uibModalInstance.dismiss('cancel');
    }
}
