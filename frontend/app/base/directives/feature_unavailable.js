angular.module('app.directives').component('featureUnavailable', {
    templateUrl: 'base/directives/feature_unavailable.html',
    bindings: {
        tier: '@',
        labelIcon: '@?',
        labelText: '@?',
        inline: '@?',
    },
    transclude: true,
});
