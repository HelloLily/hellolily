
// TODO: set focus on first element a form error was detected
// TODO: select first e-mail as primary when deleting primary

$(document).ready(function() {
    // set focus on first name
    set_focus('id_first_name');

    // manually add hover classes when hovering over a label element
    $('.email_is_primary label span').live({
        mouseenter: function() {
            $(this).addClass('state-hover');
        },
        mouseleave: function() {
            $(this).removeClass('state-hover');
        }
    });

    // change selected primary e-mailadres
    $('.email_is_primary label span').live('click', function() {
    	// find elements
        formset = $(this).closest('.mws-form-row');
        input_siblings = $(formset).find('.email_is_primary label input');

        // uncheck others
        $(input_siblings).siblings('span').removeClass('checked');

        // check this one
        $(this).addClass('checked');
    })

    // update e-mail formset to select first as primary
    // $('.email_is_primary input[name$="primary-email"]:first').attr('checked', 'checked').siblings('span').addClass('checked');
});
