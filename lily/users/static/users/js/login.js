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
	
    // set focus on username
	set_focus('id_username');
        
    $('input:checkbox').screwDefaultButtons({
        checked:    'url(/static/plugins/screwdefaultbuttons/images/checkbox_checked.png)',
        unchecked:  'url(/static/plugins/screwdefaultbuttons/images/checkbox_unchecked.png)',
        width:      16,
        height:     16
    });
});
