
// TODO: set focus on first element a form error was detected
// TODO: select first e-mail as primary when deleting primary

$(document).ready(function() {
    // set focus on website
    set_focus('id_primary_website');

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

    // delete account
    $('#delete-account-dialog-link').click(function(event) {
        $('#delete-account-form-dialog').dialog('open');
        event.preventDefault();
    });
    // transform div into delete dialog
    $('#delete-account-form-dialog').dialog({
        autoOpen: false,
        title: gettext('Delete account'),
        modal: true,
        width: 350,
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
    form_prefices = {'websites': gettext('Add a website'), 'email_addresses': gettext('Add an e-mail address'), 'phone_numbers': gettext('Add a phone number'), 'addresses': gettext('Add an address')};
    for(form_prefix in form_prefices) {
        $('.' + form_prefix + '-mws-formset').formset( {
            formTemplate: $('#' + form_prefix + '-form-template'), // needs to be unique per formset
            prefix: form_prefix, // needs to be unique per formset
            addText: form_prefices[form_prefix],
            formCssClass: form_prefix, // needs to be unique per formset
            addCssClass: form_prefix + '-add-row', // needs to be unique per formset
            added: function(row) { $.tabthisbody(); enableChosen(row); },
            deleteCssClass: form_prefix + '-delete-row', // needs to be unique per formset
            notEmptyFormSetAddCssClass: 'mws-form-item',
        });
    };

    // auto grow description
    $('#id_description').elastic();

    // update e-mail formset to select first as primary
    // $('.email_is_primary input[name$="primary-email"]:first').attr('checked', 'checked').siblings('span').addClass('checked');

    // request data to enrich form
    function do_request_to_enrich(form, domain) {

        if( $.trim(domain).length > 0 ) {
            $('#enrich-busy').show();
            $('#enrich-busy-message').text(gettext('Looking for information about') + ' ' + domain + ' ');

            msg_text = $('#enrich-busy-message').text();
            function do_busy(text, dots) {
			 	if( dots.length == 3 ) {
		            dots = '';
		       	}
		        dots += '.';
	        	$('#enrich-busy-message').text(msg_text + dots);

	        	timeout = setTimeout(function() {
	        		do_busy(msg_text, dots);
	            }, 1000);
	    	}
    		do_busy(msg_text, '');

            // try this
            var jqXHR = $.ajax({
                url: '/provide/account/' + domain,
                type: 'GET',
                dataType: 'json',
            })
            // on success
    		jqXHR.done(function(data, status, xhr) {
				dataprovider_json_to_form(data, form);

                $.jGrowl(gettext('Form has been updated with details for') + ' ' + domain, {
                    theme: 'info mws-ic-16 ic-accept'
                });
            });
	        // on error
	       	jqXHR.fail(function() {
            	$.jGrowl(gettext('No information found for') + ' ' + domain, {
                    theme: 'info mws-ic-16 ic-exclamation'
                });
            });
	        // finally do this
	       	jqXHR.always(function() {
        		clearTimeout(timeout);
            	setTimeout(function() {
            		$('#enrich-busy-message').text(gettext('Search complete.'));
            		setTimeout(function() {
        				// hide overlay
	                	$('#enrich-busy').hide();
	                	// remove request object
	                	jqXHR = null;
		            }, 500);
	            }, 1000);

            });

            $('#enrich-account-cancel').click(function(event) {
	        	// if the request is still running, abort it.
	        	if( jqXHR ) jqXHR.abort();
	        	// hide overlay
		        clearTimeout(timeout);
		        $('#enrich-busy').hide();

		        event.preventDefault();
		    });
        }
    }

    // do above request on enter key in text input and on button click
    $('#id_primary_website, #id_account_quickbutton_website').each(function() {
        $(this).keydown(function(event) {
        	// enrich on enter key
            if (event.keyCode == 13) {
            	form = $(this).closest('form');
                domain = $(this).val().replace('http://', '');
            	do_request_to_enrich(form, domain);
            	event.preventDefault();
    	    }
        });
    });
    $('#enrich-account-button, #enrich-account-quickbutton-button').each(function() {
        $(this).click(function(event) {
        	console.log('account button click');
            form = $(this).closest('form');
            domain = $(this).closest('.mws-form-row').find(':input:first').val().replace('http://', '');
        	do_request_to_enrich(form, domain);
            event.preventDefault();
        });
    });
});
