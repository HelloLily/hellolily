$(document).ready(function() {
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
	
	if($.fn.placeholder) {
		$('[placeholder]').placeholder();
	}
	
	username_el = document.getElementById('username');
	if(username_el) {
	    username_el.focus();
	}
});
