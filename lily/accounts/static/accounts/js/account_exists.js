$(document).ready(function() {
	$('form').each(function() {
		link = $(this).find('.existing-account-link');

		if( !link.length ) return true; // continue

	    var account_check_jqXHR = null;
	    var account_check_timeout = null;
	    var account_check_curval = null;
	    $(this).find('input[name="name"]').keyup(function(event) {
	        // clear any ongoing request
	        if( account_check_jqXHR ) account_check_jqXHR.abort();

	        if( account_check_curval != $.trim($(event.target).val()) ) {
	            // save input that's being sent to check existence
	            account_check_curval = $.trim($(event.target).val());

	            // prevent any calls set in the past
	            clearTimeout(account_check_timeout);

	            // hide edit link until succesful response
	            link = $(event.target).closest('form').find('.existing-account-link');
	            link.hide();
	            link.attr('href', '#');

	            // make an ajax call to check whether an account might have a duplicate
	            account_check_timeout = setTimeout(function() {

	                if( account_check_curval.length > 0 ) {

	                    // try this
	                    account_check_jqXHR = $.ajax({
	                        url: '/accounts/exists/' + account_check_curval.replace('#/g', '') + '/',
	                        type: 'GET',
	                        dataType: 'json',
	                    })
	                    // on success
	                    account_check_jqXHR.done(function(data, status, xhr) {
	                        // show edit link
	                        link.attr('href', data.edit_url);
	                        link.show();

	                        // show notification
	                        $.jGrowl(gettext('Another account was found with a similar name to') + ' ' + account_check_curval + '. ' + gettext('Follow the edit link to start editing the existing account for') + ' ' + account_check_curval + '. ', {
	                            theme: 'warning mws-ic-16 ic-error',
	                            life: 10000
	                        });
	                    });
	                    // on error
	                    account_check_jqXHR.fail(function() {
	                        link.hide();
	                        link.attr('href', '#');
	                    });
	                    // finally do this
	                    account_check_jqXHR.always(function() {
	                        clearTimeout(account_check_timeout);
	                        setTimeout(function() {
	                            // remove request object
	                            account_check_jqXHR = null;
	                        }, 500);
	                    });
	                }

	                account_check_timeout = null;
	            }, 500);
	        }
	    });
	});
});
