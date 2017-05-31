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
    var vm = this;

    var websites = vm.websites.filter(website => website.is_primary === false);

    if (!websites.length) {
        vm.addRelatedField({field: 'website'});
    }
}
