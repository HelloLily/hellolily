function ObjectLimitController() {
    const ctrl = this;

    ctrl.$onInit = () => {
        const model = ctrl.model.replace( /([A-Z])/g, ' $1').toLowerCase();

        ctrl.tooltip = sprintf(messages.tooltips.limitReached, {model});
        ctrl.isDisabled = currentUser.limitReached[ctrl.model];
    };
}

angular.module('app.directives').component('objectLimit', {
    templateUrl: 'base/directives/object_limit.html',
    controller: ObjectLimitController,
    transclude: true,
    bindings: {
        model: '@',
    },
});
