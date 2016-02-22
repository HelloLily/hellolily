angular.module('app.forms.directives').directive('formRadioButtons', formRadioButtons);

function formRadioButtons() {
    return {
        restrict: 'E',
        require: '^form',
        scope: {
            options: '=',
            labelTitle: '@',
            field: '=',
            required: '@',
            inputName: '@',
            sidebar: '=',
        },
        templateUrl: 'forms/directives/radio_buttons.html',
        controller: FormRadioButtonsController,
        controllerAs: 'vm',
        bindToController: true,
        link: function(scope, element, attrs, form) {
            // Set parent form on the scope.
            scope.form = form;
        },
    };
}

function FormRadioButtonsController() {
    var vm = this;
    vm.setValue = setValue;

    // Because we're using labels as radio buttons, we need a click handler.
    function setValue(value, $event) {
        vm.field = value;

        $event.stopPropagation();
    }
}
