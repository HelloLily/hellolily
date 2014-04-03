$(function() {
    $('body').on('shown.bs.modal', '.modal', function () {
        $(this).find('form').data('serialized_form', $(this).find('form').serialize());
    });

    $('body').on('hide.bs.modal', '.modal', function (e) {
        if ($(this).find('form').data('serialized_form') != $(this).find('form').serialize()) {
            if (!confirm('Are you sure?')) {
                e.preventDefault();
            }
        }
    });
});