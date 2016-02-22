angular.module('app.forms.directives').directive('formRadioButtons', formRadioButtons);

function formRadioButtons() {
    return {
        restrict: 'E',
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
    };
}

function FormRadioButtonsController() {
}
