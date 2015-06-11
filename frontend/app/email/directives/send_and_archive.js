angular.module('app.email.directives').directive('sendAndArchive', SendAndArchiveDirective);

SendAndArchiveDirective.$inject = ['SelectedEmailAccount'];
function SendAndArchiveDirective (SelectedEmailAccount) {
    return {
        restrict: 'A',
        link: function (scope, element) {
            element.on('click', function () {
                $('<input />').attr('type', 'hidden')
                    .attr('name', 'archive')
                    .attr('value', true)
                    .appendTo(element.closest('form'));
                if (SelectedEmailAccount.currentAccountId && SelectedEmailAccount.currentFolderId) {
                    $("input[name='success_url']").val('#/email/account/' + SelectedEmailAccount.currentAccountId + '/' + SelectedEmailAccount.currentFolderId);
                }
            });
        }
    }
}

