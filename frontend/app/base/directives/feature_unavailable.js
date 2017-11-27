function FeatureUnavailableController() {
    const ctrl = this;

    ctrl.$onInit = () => {
        if (!currentUser.isAdmin) {
            ctrl.message = sprintf(messages.tooltips.featureUnavailable, {name: currentUser.tenant.accountAdmin});
        } else {
            ctrl.message = messages.tooltips.featureUnavailableAdminText;
        }
    };
}

angular.module('app.directives').component('featureUnavailable', {
    templateUrl: 'base/directives/feature_unavailable.html',
    controller: FeatureUnavailableController,
    bindings: {
        tier: '@',
        labelIcon: '@?',
        labelText: '@?',
        inline: '@?',
    },
    transclude: true,
});
