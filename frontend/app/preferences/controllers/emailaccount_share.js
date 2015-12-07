angular.module('app.preferences').controller('EmailAccountShareModalController', EmailAccountShareModalController);

EmailAccountShareModalController.$inject = ['$uibModalInstance', '$scope', 'EmailAccount', 'User', 'currentAccount'];
function EmailAccountShareModalController ($uibModalInstance, $scope, EmailAccount, User, currentAccount) {
    $scope.currentAccount = currentAccount;

    // Get all users to display in a list
    User.query({}, function(data) {
        $scope.users = [];
        // Check if user has the emailaccount already shared
        angular.forEach(data, function(user) {
            if ($scope.currentAccount.shared_with_users.indexOf(user.id) !== -1) {
                user.sharedWith = true;
            }
            $scope.users.push(user);
        });
    });

    $scope.ok = function () {
        // Save updated account information
        if ($scope.currentAccount.public) {
            EmailAccount.update({id: $scope.currentAccount.id}, $scope.currentAccount, function() {
                $uibModalInstance.close();
            });
        } else {
            // Get ids of the users to share with
            var shared_with_users = [];
            angular.forEach($scope.users, function(user) {
                if(user.sharedWith) {
                    shared_with_users.push(user.id);
                }
            });
            // Push ids to api
            EmailAccount.shareWith({id: $scope.currentAccount.id}, {shared_with_users: shared_with_users}, function() {
                $uibModalInstance.close();
            });
        }
    };

    // Lets not change anything
    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}
