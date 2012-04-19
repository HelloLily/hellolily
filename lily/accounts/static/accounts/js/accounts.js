
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
        formset = $(this).closest('.mws-form-row');
        input_siblings = $(formset).find('.email_is_primary label input');
        
        // uncheck others
        $(input_siblings).siblings('span').removeClass('checked');
        
        // check this one
        $(this).addClass('checked');
    })
    
    // show or hide 'other'-options on page load or when the value changes
    $('select.other:visible').each(function() {
        show_or_hide_other_option($(this)[0], true);
    }).live('change', function() {
        show_or_hide_other_option($(this)[0]);
    });
    
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
                'class': 'mws-button red float-left',
                text: gettext('Cancel'),
                click: function() {
                    $(this).dialog('close');
                }
            },
            {
                'class': 'mws-button green',
                text: gettext('Add & edit'),
                click: function() {
                    // set form input to edit so we get a redirect to the extendend edit page
                    $('#add-account-submit').val('edit');
                    sendForm( $(this) );
                },
                name: 'submit',
                value: 'edit'
            },
            {
                'class': 'mws-button green',
                text: gettext('Add'),
                click: function() {
                    sendForm( $(this) );
                },
                name: 'submit',
                value: 'add'
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
    form_prefices = ['websites', 'email_addresses', 'phone_numbers', 'addresses'];    
    $.each(form_prefices, function(index, form_prefix) {
        $('.' + form_prefix + '-mws-formset').formset( {
            formTemplate: $('#' + form_prefix + '-form-template'), // needs to be unique per formset
            prefix: form_prefix, // needs to be unique per formset
            addText: gettext('Add another'),
            formCssClass: form_prefix, // needs to be unique per formset
            addCssClass: form_prefix + '-add-row add-row mws-form-item', // needs to be unique per formset
            deleteCssClass: form_prefix + '-delete-row' // needs to be unique per formset
        });
    });
    
    // update e-mail formset to select first as primary
    // $('.email_is_primary input[name$="primary-email"]:first').attr('checked', 'checked').siblings('span').addClass('checked'); 
});
