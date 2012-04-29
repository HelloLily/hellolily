
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
    
    // show or hide 'other'-options on page load or when the value changes
    $('select.other:visible').each(function() {
        show_or_hide_other_option($(this)[0], true);
    }).live('change', function() {
        show_or_hide_other_option($(this)[0]);
    });
    
    // show delete-form-dialog
    $('#delete-contact-dialog-btn').click(function(event) {
        $('#delete-contact-form-dialog').dialog('open');
        event.preventDefault();
    });  
    
    // add jquery dialog for adding an account
    $('#delete-contact-form-dialog').dialog({
        autoOpen: false,
        title: gettext('Delete contact'),
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
    form_prefices = {'email_addresses': gettext('Add an e-mail address'), 'phone_numbers': gettext('Add a phone number'), 'addresses': gettext('Add an address')};    
    for(form_prefix in form_prefices) {
        $('.' + form_prefix + '-mws-formset').formset( {
            formTemplate: $('#' + form_prefix + '-form-template'), // needs to be unique per formset
            prefix: form_prefix, // needs to be unique per formset
            addText: form_prefices[form_prefix],
            formCssClass: form_prefix, // needs to be unique per formset
            addCssClass: form_prefix + '-add-row', // needs to be unique per formset
            deleteCssClass: form_prefix + '-delete-row', // needs to be unique per formset
            notEmptyFormSetAddCssClass: 'mws-form-item'
        });
    };
    
    // auto grow description 
    $('#id_description').autoGrow({
        cols: 60,
        rows: 1
    });
    
    // update e-mail formset to select first as primary
    // $('.email_is_primary input[name$="primary-email"]:first').attr('checked', 'checked').siblings('span').addClass('checked');
    
    $(".mws-tabs").tabs();
    
    // add jquery dialog for adding an account
    $('#delete-contact-form-dialog').dialog({
        autoOpen: false,
        title: gettext('Delete contact'),
        modal: true,
        width: 640,
        buttons: [
            { 
                'class': 'mws-button red float-left',
                text: gettext('Cancel'),
                click: function() {
                    // cancel form on NO
                    $(this).dialog('close');
                }
            },
            {
                'class': 'mws-button green',
                text: gettext('Continue'),
                click: function() {
                    // submit form on YES
                    $(this).find('form').submit();
                }
            }
        ]
    });
    
    // show delete-form-dialog
    $('#delete-contact-dialog-link').click(function(event) {
        $('#delete-contact-form-dialog').dialog('open');
        event.preventDefault();
    });
    
    // add jquery dialog for adding an account
    $('#delete-note-form-dialog').dialog({
        autoOpen: false,
        title: gettext('Delete note'),
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
                text: gettext('Continue'),
                click: function() {
                    var successCallback = function(response, hideLoadingDialog) {
                        if( response.error === true ) {
                            // Request was successfull but the form returned with errors
                            $(form).html(response.html);
                            if( typeof bindFormset == typeof Function )
                                bindFormset();
                            $('#loadingDialog').dialog('close');
                            $(dialog).dialog('open');
                        } else if( response.redirect === true ) {
                            // The page is redirected, follow the redirect
                            window.location = response.url
                        } else {
                            // Everything worked, handle the success response
                            afterSuccess = function() {
                                var link = $('.object-list-item.note a[href="' + $('#delete-note-form-dialog #delete-note-form').attr('action') + '"]');
                                var div = link.closest('.object-list-item.note');
                                div.slideUp(500, function() {
                                    div.remove(); 
                                });
                            };
                            hideLoadingDialog(afterSuccess);
                        }
                    }
                    sendForm($(this), successCallback);
                }
            }
        ]
    });
    
    // show delete-form-dialog
    $('.delete-note-dialog-link').click(function(event) {
        $('#delete-note-form-dialog #delete-note-form').attr('action', $(this).attr('href'));
        $('#delete-note-form-dialog').dialog('open');
        event.preventDefault();
    });
    
    // auto grow description 
    $('.autogrow').autoGrow({
        cols: 60
    });
    
    // submit the form on ctrl + enter
    $('textarea').keydown(function(event) {
    	form = $(this).closest('form');
    	submit_form_on_ctrl_enter(event, form);
    });
    
    var editNoteListener = function(elem) {
        note = $(elem).closest('.note');
        textarea = note.find('textarea');
        text = note.find('.object-list-item-text:visible:first');
        
        // copy original content into textarea
        $(textarea).val($.trim(text.text()));
    };
    
    $('.object_edit_link').live('click', function() {
        editNoteListener($(this));
    });
    
    // simply clear the form on cancel
    $('.object_cancel_link').live('click', function() {
        clearForm($(this).closest('.iedit_wrapper').find('form'));
    });
    
    // use AJAX when submitting
    $('.note form').submit(function() {
    	// find the container
    	container = $(this).closest('.iedit_wrapper');
        
        // do this on success
        var successCallback = function(response, hideLoadingDialog) {
            // Show the succes image at the right side of the note
            container.html(response.html);
            
            if( response.error === true ) {
                // Request was successfull but the form returned with errors
                container.find('.iedit_content .iedit_button').click();
            } else {
                // Everything worked, handle the success response
                container.find('.object-list-ajax-message.loading').fadeOut(400, function() {
                    container.find('.object-list-ajax-message.success').fadeIn(400);
                });
                
                container.find('.object-list-ajax-message.success').delay(5000).fadeOut(400);
            }
            container.find('.autogrow').autoGrow({
                cols: 60
            });
        };
        
        // do this on errors
        var errorCallback = function() {
            // Show the error image at the right side of the note
            container.find('.iedit_form .iedit_button').click();
            container.find('.object-list-ajax-message.loading').fadeOut(400, function() {
                container.find('.object-list-ajax-message.error').fadeIn(400);
            });
        };
        
    	// always do this
        var beforeSubmit = function() {
            container.find('.object-list-ajax-message.loading').fadeIn(400);
        };
        
        // submit form through AJAX
        sendForm(container, successCallback, errorCallback, beforeSubmit);
        
        // dont follow form's action
        return false;
    });
    
    // submit the closest form when clicking this 
    $('.iedit_submit_button').live('click', function() {
    	// submit form by pressing this button/anchor
    	form = $(this).closest('.note').find('form');
    	form.submit();
    	
    	// don't follow button/anchor's href
        return false;
    });
});
