$(document).ready(function() {
    // set focus on company name
    set_focus('id_name'); 
    
    // TODO: set focus on first element a form error was detected
    
    // manually add hover classes when hovering over a label element
    $('.email_is_primary label').live({
        mouseenter: function() {
            $(this).addClass('state-hover');
        },
        mouseleave: function() {
            $(this).removeClass('state-hover');
        }
    });
    
    // change selected primary e-mailadres
    $('.email_is_primary label span').live('click', function() {
        siblings = $(this).parent().parent().siblings().find('label.checked');
        $(siblings).removeClass('checked');
        $(this).parent().addClass('checked');
        
        // TODO: decide whether to use this or not
        // Remove delete button for primary e-mail addresses
        // $(siblings).each(function(index, element) {
            // button = $(element).parent().parent().next('div').find('#' + $(element).find('input').val());
            // button.show();
        // });
        // button = $(this).parent().parent().next('div').find('#' + $(this).find('input').val());
        // button.hide();
    })
    
    // show or hide an input field for the user to input an option manually when the 'other'-option
    // has been selected in a select element.
    $('select.other').live('change', function() {
        form_index = $(this).attr('id').replace(/[^\d.]/g, '');
        form_prefix = $(this).attr('id').substr(0, $(this).attr('id').indexOf(form_index) - 1);
        select_fieldname = $(this).attr('id').replace(form_prefix + '-' + form_index + '-', '');
        
        // show/hide input field
        other_type_input = $('#' + form_prefix + '-' + form_index + '-other_' + select_fieldname);
        if( $(this).val() == 'other' ) {
            other_type_input.show();
        } else {
            other_type_input.hide();
        }
    });
    
    // show add-form-dialog
    $('#open-account-dialog-btn').click(function(event) {
        $('#account-form-dialog').dialog('open');
        event.preventDefault();
    });    
    
    // add jquery dialog for adding an account
    $('#account-form-dialog').dialog({
        autoOpen: false,
        title: gettext('New account'),
        modal: true,
        width: 640,
        buttons: [
            { 
                text: gettext('Cancel'),
                click: function() {
                    $(this).dialog('close');
                }
            },
            {
                text: gettext('Add & edit'),
                click: function() {
                    sendForm( $(this) );
                }
            },
            {
                text: gettext('Add'),
                click: function() {
                    sendForm( $(this) );
                }
            },
        ],
        close: function() {
            clearForm( $(this).find('form') );
        }
    });
});
