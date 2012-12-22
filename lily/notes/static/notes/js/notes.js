$(document).ready(function() {
	// add jquery dialog for adding an account
    $('#dialog-delete-note').dialog({
        autoOpen: false,
        modal: true,
        width: 350,
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
                                var link = $('.object-list-item.note a[href="' + $('#dialog-delete-note form').attr('action') + '"]');
                                var div = link.closest('.object-list-item.note');
                                div.slideUp(500, function() {
                                    div.remove(); 
                                });
                                $(div).find('textarea').elastic();
                            };
                            hideLoadingDialog(afterSuccess);
                        }
                    }
                    sendForm($(this), successCallback);
                }
            }
        ]
    });
    
    var editNoteListener = function(elem) {
        note = $(elem).closest('.note');
        textarea = note.find('textarea');
        text = note.find('.object-list-item-text:first');
        $(textarea).trigger('change');
        $(textarea).val($.trim(text.text()));
        $.tabthisbody();
    };
    
    // edit note
    $('.note .object_edit_link').live('click', function() {
        editNoteListener($(this));
    });
    
    // save note
    $('.note .iedit_submit_button').live('click', function(event) {
    	// submit form by pressing this button/anchor
    	form = $(this).closest('.note').find('form');
    	form.submit();
    	
    	// don't follow button/anchor's href
        event.preventDefault();
    });
    
    // delete note
    $('.delete.note').live('click', function(event) {
        $('#dialog-delete-note form').attr('action', $(this).attr('href'));
        $('#dialog-delete-note').dialog('open');
        
        // don't follow button/anchor's href
        event.preventDefault();
    });
    
    // submit note with AJAX
    $('.note form').live('submit', function(event) {
    	// find the container
    	container = $(this).closest('.iedit_wrapper');
        
        // do this on success
        var successCallback = function(response, hideLoadingDialog) {
            // Show the succes image at the right side of the note
            container.html(response.html);
            
            if( response.error === true ) {
                // Request was successful but the form returned with errors
                container.find('.iedit_content .iedit_button').click();
            } else {
                // Everything worked, handle the success response
                container.find('.object-list-ajax-message.loading').fadeOut(400, function() {
                    container.find('.object-list-ajax-message.success').fadeIn(400);
                });
                
                container.find('.object-list-ajax-message.success').delay(5000).fadeOut(400);
            }
            
            container.find('.note-autogrow').elastic();
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
        event.preventDefault();
    });
});
