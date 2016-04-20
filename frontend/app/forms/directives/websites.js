angular.module('app.forms.directives').directive('formWebsites', formWebsites);

function formWebsites() {
    return {
        restrict: 'E',
        require: '^form',
        scope: {
            websites: '=',
            addRelatedField: '&',
            removeRelatedField: '&',
            doubleAccountCheck: '&',
        },
        templateUrl: 'forms/directives/websites.html',
        controller: FormWebsitesController,
        controllerAs: 'vm',
        bindToController: true,
        link: function(scope, element, attrs, form) {
            // Set parent form on the scope
            scope.form = form;
        },
    };
}

FormWebsitesController.$inject = [];
function FormWebsitesController() {

}
