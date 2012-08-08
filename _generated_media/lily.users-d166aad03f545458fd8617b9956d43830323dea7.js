$(document).ready(function() {
    // set focus on e-mail address
    set_focus('id_email');
});



$(document).ready(function() {
    function bindFormset() {
        $('.mws-form-formset').formset({
            formTemplate: '.formset-custom-template',
            prefix: 'form',
            addText: gettext('Add another'),
            preventEmptyFormset: true,
            added: function() { $.tabthisbody(); },
            addCssClass: 'add-row mws-form-row',
            deleteCssClass: 'invitation-delete-row',
        });
    }
    bindFormset();
    
    $("#mws-form-dialog").dialog({
        autoOpen: false, 
        title: gettext('User invitation form'), 
        modal: true, 
        width: "640", 
        buttons: [{
            text: gettext('Send invitation(s)'), 
            click: function() { sendForm($( this )); }
        }],
        close: function(event, ui) { clearForm($(this).find('form.mws-form')); }
    });
    
    $("#mws-form-dialog-mdl-btn").bind("click", function(event) {
        $("#mws-form-dialog").dialog("open");
        event.preventDefault();
    });
});

$(document).ready(function() {
    // form validator
	$.validator.addMethod("placeholder", function(value, element) {
	  return value != $(element).attr("placeholder");
	}, $.validator.messages.required);
	
	$("#mws-login-form form").validate({
		rules: {
			username: {required: true, placeholder: true}, 
			password: {required: true, placeholder: true}
		}, 
		errorPlacement: function(error, element) {  
		}, 
		invalidHandler: function(form, validator) {
			if($.fn.effect) {
				$("#mws-login").effect("shake", {distance: 6, times: 2}, 35);
			}
		}
	});
	
	// form placeholder
	if($.fn.placeholder) {
		$('[placeholder]').placeholder();
	}
	
    // set focus on e-mail
	set_focus('id_username');
        
    $('input:checkbox').screwDefaultButtons({
        checked:    'url(' + media_url('plugins/screwdefaultbuttons/images/checkbox_checked.png') + ')',
        unchecked:  'url(' + media_url('plugins/screwdefaultbuttons/images/checkbox_unchecked.png') + ')',
        width:      16,
        height:     16
    });
});


$(document).ready(function() {
    // set focus on e-mail address
    set_focus('id_email');
    
    // set focus on first password input
    set_focus('id_new_password1');
});

$(document).ready(function() {
    // set focus on first name field
    set_focus('id_first_name');
    
    var error_lists = $('.errorlist');
    if(error_lists.length) {
        var first = error_lists[0];
        var input = jQuery(first).nextAll('input').eq(0);
        input.focus();
    }
})