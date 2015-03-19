$(function() {
    $('body').on('shown.bs.modal', '.modal', function () {
        $(this).find('form').data('serialized_form', $(this).find('form').serialize());
    });

    $('body').on('hide.bs.modal', '.modal', function (e) {
        // this check is to make sure not every widget with a popup displays the confirm message
        if ($(e.target).hasClass('modal') && $(this).has('form').length) {
            if ($(this).find('form').data('serialized_form') != $(this).find('form').serialize()) {
                if (!confirm('Are you sure?')) {
                    e.preventDefault();
                }
            }
        }
    });
});
