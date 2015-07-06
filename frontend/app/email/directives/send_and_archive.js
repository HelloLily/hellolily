angular.module('app.email.directives').directive('sendAndArchive', SendAndArchiveDirective);

SendAndArchiveDirective.$inject = [];
function SendAndArchiveDirective () {
    return {
        restrict: 'A',
        link: function (scope, element) {
            element.on('click', function () {
                $('<input />').attr('type', 'hidden')
                    .attr('name', 'archive')
                    .attr('value', true)
                    .appendTo(element.closest('form'));
            });
        }
    }
}
