
// TODO: set focus on first element a form error was detected    
// TODO: select first e-mail as primary when deleting primary

$(document).ready(function() {
    // set focus on company name
    set_focus('id_name'); 
    
    
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
    
    // show or hide 'other'-options on page load or when the value changes
    $('select.other').each(function() {
        show_or_hide_other_option($(this)[0], true);
    }).live('change', function() {
        show_or_hide_other_option($(this)[0]);
    });
    
    // show or hide an input field for the user to input an option manually when the 'other'-option
    // has been selected in a select element.
    function show_or_hide_other_option(select, page_load) {
    	form_index = $(select).attr('id').replace(/[^\d.]/g, '');
        form_prefix = $(select).attr('id').substr(0, $(select).attr('id').indexOf(form_index) - 1);
        select_fieldname = $(select).attr('id').replace(form_prefix + '-' + form_index + '-', '');
        
        // show/hide input field
        other_type_input = $('#' + form_prefix + '-' + form_index + '-other_' + select_fieldname);
    	if( $(select).val() == 'other' ) {
            other_type_input.show();
            if( !page_load ) {
            	other_type_input.focus();
            }
        } else {
            other_type_input.hide();
        }
    }
    
    // show add-form-dialog
    $('#add-account-dialog-btn').click(function(event) {
        $('#add-account-form-dialog').dialog('open');
        event.preventDefault();
    });
    
    // add jquery dialog for adding an account
    $('#add-account-form-dialog').dialog({
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
    
    // show delete-form-dialog
    $('#delete-account-dialog-btn').click(function(event) {
        $('#delete-account-form-dialog').dialog('open');
        event.preventDefault();
    });  
    
    // add jquery dialog for adding an account
    $('#delete-account-form-dialog').dialog({
        autoOpen: false,
        title: gettext('Delete account'),
        modal: true,
        width: 640,
        buttons: [
            { 
                'class': 'mws-button red float-left',
                text: gettext('No'),
                click: function() {
                    // cancel form on NO
                    $(this).dialog('close');
                }
            },
            {
                'class': 'mws-button green',
                text: gettext('Yes'),
                click: function() {
                    // submit form on YES
                    $(this).find('form').submit();
                }
            }
        ]
    });
    
    // enable formsets for email addresses, phone numbers and addresses
    form_prefices = ['email_addresses', 'phone_numbers', 'addresses'];    
    $.each(form_prefices, function(index, form_prefix) {
        $('.' + form_prefix + '-mws-formset').formset( {
            formTemplate: $('#' + form_prefix + '-form-template'), // needs to be unique per formset
            prefix: form_prefix, // needs to be unique per formset
            addText: gettext('Add another'),
            formCssClass: form_prefix, // needs to be unique per formset
            addCssClass: form_prefix + '-add-row add-row', // needs to be unique per formset
            deleteCssClass: form_prefix + '-delete-row' // needs to be unique per formset
        });
    });
    
    // update e-mail formset to select first as primary
    // $('.email_is_primary input[name="primary-email"]:first').attr('checked', 'checked').siblings('span').addClass('checked'); 
});
