angular.module('app.preferences').controller('PreferencesSetTemplateDefaultModal', PreferencesSetTemplateDefaultModal);

PreferencesSetTemplateDefaultModal.$inject = ['$http', '$modalInstance', '$scope', 'emailTemplate'];
function PreferencesSetTemplateDefaultModal ($http, $modalInstance, $scope, emailTemplate) {
    $scope.emailTemplate = emailTemplate;

    $scope.ok = function () {
        $http({
            url: '/messaging/email/templates/set-default/' + $scope.emailTemplate.id + '/',
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            data: $.param({id: $scope.emailTemplate.id})
        }).success(function() {
            $modalInstance.close($scope.emailTemplate);
        });
    };

    // Lets not change anything
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
}
