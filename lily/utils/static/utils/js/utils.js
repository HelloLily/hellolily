$(function() {
    /* show and hide form fields using two links with different data-action attributes */
    $('body').on('click', '.form .toggle-original-form-input', function() {
        var field = $(this).closest('.show-and-hide-input');

        /* hide clicked link */
        $(this).addClass('hide');

        /* toggle form input */
        if($(this).data('action') == 'show') {
            /* show the other link */
            $(field).find('[data-action="hide"]').removeClass('hide');

            /* show the form input */
            $(field).find('.original-form-widget').removeClass('hide');

            /* (re)enable fields */
            $(field).find(':input').removeAttr('disabled');
        } else if($(this).data('action') == 'hide') {
            /* show the other link */
            $(field).find('[data-action="show"]').removeClass('hide');

            /* hide the form input */
            $(field).find('.original-form-widget').addClass('hide');

            /* disabled fields will not be posted */
            $(field).find(':input').attr('disabled', 'disabled');
        }
    });
});
