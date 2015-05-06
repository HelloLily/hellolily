angular.module('app.forms.directives').directive('formWebsites', formWebsites);

function formWebsites() {
    return {
        restrict: 'E',
        scope: {
            websites: '=',
            addRelatedField: '&',
            removeRelatedField: '&'
        },
        templateUrl: 'forms/directives/websites.html',
        controller: FormWebsitesController,
        controllerAs: 'vm',
        bindToController: true
    }
}

function FormWebsitesController() {
    var vm = this;
}
