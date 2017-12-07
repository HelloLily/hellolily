angular.module('app.directives').directive('editableHandler', editableHandler);

function editableHandler() {
    return {
        restrict: 'A',
        link: (scope, element, attrs) => {
            let form;

            if (scope.hasOwnProperty('$form')) {
                form = scope.$form;
            } else {
                form = scope[attrs.eForm];
            }

            element.on('click', event => {
                const selection = window.getSelection().toString();
                const elementName = event.originalEvent.target.localName;

                // Allow users to select the field without opening the edit form.
                // Don't open the edit form if we're clicking a link.
                if (!selection && elementName !== 'a') {
                    form.$show();
                    scope.$apply();
                }
            });

            element.on('click', '.hl-edit-icon', event => {
                form.$show();
                scope.$apply();
            });
        },
    };
}
