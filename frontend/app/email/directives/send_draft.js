angular.module('app.email.directives').directive('sendDraft', SendDraftDirective);

SendDraftDirective.$inject = [];
function SendDraftDirective() {
    return {
        restrict: 'A',
        link: function(scope, element) {
            element.on('click', function() {
                $('<input />').attr('type', 'hidden')
                    .attr('name', 'send_draft')
                    .attr('value', true)
                    .appendTo(element.closest('form'));
            });
        }};
}
