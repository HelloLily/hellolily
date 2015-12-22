angular.module('app.contacts.directives').directive('contactListWidget', ContactListWidget);

function ContactListWidget() {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            title: '@',
            list: '=',
            height: '=',
            accountId: '@',
            addLink: '@',
        },
        templateUrl: 'contacts/directives/list_widget.html',
    };
}
