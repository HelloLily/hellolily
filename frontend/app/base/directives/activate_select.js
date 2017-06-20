angular.module('app.directives').directive('activateSelect', activateSelect);

function activateSelect($timeout) {
    return {
        restrict: 'A',
        require: '?uiSelect',
        link: function(scope, element, attrs, $select) {
            // TODO: Once Select2 implements default select behaviour we can convert all
            // current normal selects to Select2. After that we can uncomment this code
            // and make it so selects automatically get opened when inline editing.
            // Note: When building the app minified look out for the following error:
            // vendor.js:6 Error: [$injector:unpr] Unknown provider: rProvider <- r <- activateSelectDirective
            // This doesn't happen when building normally (and not sure if it happens on live.), but something
            // that needs to be looked at.
            // scope.$watch('$form.$visible', function() {
            //     $timeout(function() {
            //         Open the select on the next digest cycle.
            //         if ($select) {
            //             $select.activate();
            //         }
            //     });
            // });
        },
    };
}
