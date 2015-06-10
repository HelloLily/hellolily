angular.module('app.directives').directive('saveAndArchive', saveAndArchiveDirective);

function saveAndArchiveDirective () {
    return {
        restrict: "A",
        link: function(scope, elem, attrs) {

            // Setting button to right text based in archived state
            var $button = $('#archive-button');
            var $archiveField = $('#id_is_archived');
            if ($archiveField.val() === 'True') {
                $button.find('span').text('Save and Unarchive');
            } else {
                $button.find('span').text('Save and Archive');
            }

            // On button click set archived hidden field and submit form
            elem.on('click', function () {
                $button = $('#archive-button');
                $archiveField = $('#id_is_archived');
                var $form = $($button.closest('form').get(0));
                var archive = ($archiveField.val() === 'True' ? 'False' : 'True');
                $archiveField.val(archive);
                $button.button('loading');
                $form.find(':submit').click();
                event.preventDefault();
            });
        }
    }
}
