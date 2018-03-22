SuggestionsController.$inject = ['$scope'];
function SuggestionsController($scope) {
    const ctrl = this;

    ctrl.$onInit = () => {
        // Convert camelCase to normal spaced word.
        let label = ctrl.field.replace(/([A-Z])/g, ' $1').toLowerCase();
        // Uppercase the first letter.
        ctrl.label = label.charAt(0).toUpperCase() + label.slice(1);

        // Model is the plural version of the given type.
        ctrl.model = ctrl.type + 's';

        ctrl.isSidebar = $scope.$parent.settings.email.sidebar.form;
    };

    ctrl.getDetailSref = suggestion => {
        const stateName = `base.${ctrl.model}.detail`;

        return `${stateName}({id: ${suggestion[ctrl.type].id}})`;
    };

    ctrl.getFormSref = suggestion => {
        const stateName = `base.${ctrl.model}.detail.edit`;

        // Since the string will get parsed by ui-router, we can just create the string in the controller.
        if (ctrl.object) {
            return `${stateName}({id: ${suggestion[ctrl.type].id}, ${ctrl.type}Form: $ctrl.object})`;
        }

        return `${stateName}({id: ${suggestion[ctrl.type].id}})`;
    };

    ctrl.clickCallback = suggestion => {
        ctrl.callback()(suggestion[ctrl.type]);
    };
}

angular.module('app.directives').component('suggestions', {
    templateUrl: 'base/directives/suggestions.html',
    controller: SuggestionsController,
    bindings: {
        suggestions: '<',
        display: '=',
        field: '@',
        type: '@',
        callback: '&?',
        object: '<?',
    },
});
