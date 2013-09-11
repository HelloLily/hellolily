function clearForm(form) {

    $(form).clearForm();
    $(form).find('.mws-error').remove();
    $(form).find('.field_error').each(function(index, element) {
       $(element).removeClass('field_error');
    });
}

// TODO: detect which button was clicked to be able to redirect to an edit view
function sendForm(dialog, successCallback, errorCallback, beforeSubmit) {
    var form = $(dialog).find('form')[0],
        counter = 0,
        cb = null;

    var hideLoadingDialog = function(callback) {
        counter++;
        if(callback){ cb = callback; }
        if(counter === 2) {
            $('#loadingDialog').dialog('close');
            clearForm(form);
            $(dialog).dialog('close');
            cb();
        }
    };

    $(form).ajaxSubmit({
        type: 'post',
        dataType: 'json',
        url: $(dialog).attr('action'),
        data: {
            'csrfmiddlewaretoken': dialog.find('input[name="csrfmiddlewaretoken"]').val()
        }, beforeSubmit: function() {
            if(!beforeSubmit) {
                $(form).dialog('close');
                $('#loadingDialog').dialog('open');
                    setTimeout(function() {
                        hideLoadingDialog();
                    }, 1200);
            } else {
                beforeSubmit();
            }
        }, success: function(response) {
            if(!successCallback){
                if( response.error === true ) {
                    // Request was successfull but the form returned with errors
                    $(form).html(response.html);
                    if( typeof bindFormset == typeof Function )
                        bindFormset();
                    enableChosen(dialog);
                    $('#loadingDialog').dialog('close');
                    $(dialog).dialog('open');
                } else if( response.redirect === true ) {
                    // The page is redirected, follow the redirect
                    window.location = response.url
                } else {
                    // Everything worked, handle the success response
                    afterSuccess = function() {
                        if( response.html.length ) {
                            $('#successDialogMessage').text(response.html);
                            $('#successDialog').dialog('open');
                        }

                        if( $.jGrowl ) {
                            if( response.notification ) {
                                for(i=0; i < response.notification.length; i++) {
                                    $.jGrowl(response.notification[i].message, {
                                        theme: response.notification[i].tags
                                    });
                                }
                            }
                        }
                    };
                    hideLoadingDialog(afterSuccess);
                }
            } else {
                successCallback(response, hideLoadingDialog);
            }
        }, error: function(){
            if(!errorCallback){
                errorCallback = function() {
                    $(dialog).dialog('close');
                    $('#errorDialog').dialog('open');
                };
                hideLoadingDialog(errorCallback);
            }
            errorCallback();
        }
    });
}
