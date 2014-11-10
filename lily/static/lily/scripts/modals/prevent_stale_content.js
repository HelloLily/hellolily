$(function() {
    $('body').on('hidden.bs.modal', '.modal', function (e) {
        // this check is to make sure not every widget with a popup displays the confirm message
        if ($(e.target).hasClass('modal')) {
            $(this).html('');
        }
    });

    $('body').on('shown.bs.modal', '.modal', function (e) {
        // this check is to make sure not every widget with a popup displays the confirm message
        if ($(e.target).hasClass('modal') && $(this).html() === '') {
            // close modal
            $(this).modal('hide');
            // show toastr message
            toastr.error(gettext('Oops.. something went wrong :('));
        }
    });
});
