function clearForm(form) {
    $(form).clearForm();
    $(form).find('.mws-error').remove();
}

function sendForm(popup) {
    var form = $( popup ).find('form.mws-form')
    if (typeof(form === 'list')){ form = form[0]; }
    
    var hideLoadingDialog = (function() {
        var counter = 0;
        
        return function() {
            counter++;
            if (counter === 2) {
                $("#loadingDialog").dialog("close");
                clearForm(form);
            }
        };
    })();
    
    setTimeout(function() {
        hideLoadingDialog();
    }, 1500);
    
    $(form).ajaxSubmit({
        type: 'post',
        dataType: 'json',
        url: $(form).attr('action'),
        data: {
            'csrfmiddlewaretoken': popup.find('input[name="csrfmiddlewaretoken"]').val()
        }, beforeSubmit: function() {
            $("#mws-form-dialog").dialog("close");
            $("#loadingDialog").dialog("open");
        }, success: function(response) {
            if (response.error === true) {
                $(form).html(response.html);
                bindFormset();
                $("#loadingDialog").dialog("close");
                $("#mws-form-dialog").dialog("open");
            } else {
                hideLoadingDialog();
                $("#successDialogMessage").text(response.html);
                $("#mws-form-dialog").dialog("close");
                $("#successDialog").dialog("open");
            }
        }, error: function(){
            $("#errorDialog").dialog("open");
        }
    });
}
