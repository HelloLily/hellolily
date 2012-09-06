$(document).ready(function() {
	// form template to copy
	var form_html = $('<div>').append($('#microblog form:first').clone()).html();
	
	// insert form template into dom on click
	$('.blogentry-reply').live('click', function(event) {
		// remove others
		$('#blogentries form').remove();

		// set id of entry replying to
		var parent_blogentry_id = $(event.target).closest('.blogentry').data('entry-id')
		var blogentry = $(this).closest('.blogentry');

		$(blogentry).append($(form_html).clone());
		$(blogentry).find('input[name="reply_to"]').val(parent_blogentry_id);
		$(blogentry).find('form textarea').next('div').remove();
		$(blogentry).find('form textarea').elastic();
		
		$(blogentry).find('form').slideDown('fast');
		$(blogentry).find('form textarea').focus();
		
		event.preventDefault();
	});
	
	$('#blogentries .replied-to').live('click', function(event) {
		$('#blogentries .perma-marked').removeClass('perma-marked');
		$('#blogentries .origin').removeClass('origin');
		$('#entry-' + $(event.target).data('replied-to')).addClass('perma-marked');
		$(event.target).closest('.blogentry').addClass('origin');
     });
	
	$('#blogentries .replied-to').live({
        mouseover: function() {
			$('#entry-' + $(this).data('replied-to')).addClass('marked');
        },
        mouseout: function() {
			$('#entry-' + $(this).data('replied-to')).removeClass('marked');
        }
     });
     
     // delete via ajax and reload if success
     $('#blogentries .blogentry-delete').live('click', function(event) {
		var blogentry_id = $(event.target).closest('.blogentry').data('entry-id');
		
		// try this
        var jqXHR = $.ajax({
            url: '/updates/delete/' + blogentry_id + '/',
            type: 'POST',
            beforeSend: addCSRFHeader,
            dataType: 'json',
        })
        // on success
        jqXHR.done(function(data, status, xhr) {
        	if( data.redirect === true ){
        		window.location = data.url
        	}
        });
        // on error
        jqXHR.fail(function() {
            $.jGrowl(gettext('Post could not be deleted'), {
                theme: 'info mws-ic-16 ic-error'
            });
        });
        // finally do this
        jqXHR.always(function() {
            // remove request object
            jqXHR = null;
        });
		
		event.preventDefault();
     });
});