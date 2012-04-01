$(document).ready(function() {
    // set focus on company name
    set_focus('id_name'); 
    
    // TODO: set focus on first element a form error was detected
    
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
    	formset = $(this).parentsUntil('.mws-form-row', '.mws-formset');
        input_siblings = $(formset).siblings().find('.email_is_primary label input');
        
        // uncheck others
        $(input_siblings).siblings('span').removeClass('checked');
        
        // check this one
        $(this).addClass('checked');
    })
    
    // TODO: select first e-mail as primary when deleting primary
    
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
            other_type_input.focus();
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
    
    // enable formsets
    $('.mws-formset').each(function(index, formset) {
        form_index = $(this).attr('id').replace(/[^\d.]/g, '');
        form_prefix = $(this).attr('id').substr(0, $(this).attr('id').indexOf(form_index) - 1);
    	$(formset).formset( {
            prefix: form_prefix,
            addText: gettext('Add another'),
            preventEmptyFormset: true
    	});
    });
    
    // update e-mail formset to select first as primary
    $('.email_is_primary input[name="primary-email"]:first').attr('checked', 'checked').siblings('span').addClass('checked'); 
});
