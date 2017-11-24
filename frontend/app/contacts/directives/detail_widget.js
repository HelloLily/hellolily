angular.module('app.contacts.directives').directive('contactDetailWidget', contactDetailWidget);

function contactDetailWidget() {
    return {
        restrict: 'E',
        scope: {
            contact: '=',
            height: '=',
            updateCallback: '&',
            clickableHeader: '=?',
        },
        templateUrl: 'contacts/directives/detail_widget.html',
        controller: ContactDetailWidgetController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

ContactDetailWidgetController.$inject = ['Contact', 'Settings'];
function ContactDetailWidgetController(Contact, Settings) {
    const vm = this;

    vm.settings = Settings;

    vm.updateModel = updateModel;

    activate();

    ////

    function activate() {
        if (typeof vm.clickableHeader === 'undefined') {
            vm.clickableHeader = true;
        }
    }

    function updateModel(data, field) {
        return Contact.updateModel(data, field, vm.contact);
    }
}

