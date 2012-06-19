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

$(document).ready(function() {
    // do do_request_to_enrich() on enter key in text input 
    $('#id_primary_website, #id_account_quickbutton_website').each(function() {
        $(this).keydown(function(event) {
            // enrich on enter key only
            if (event.keyCode == 13) {
                form = $(this).closest('form');
                domain = $(this).val().replace('http://', '');
                do_request_to_enrich(form, domain);
                event.preventDefault();
            }
        });
    });
    // do do_request_to_enrich() on button click
    $('#enrich-account-button, #enrich-account-quickbutton').each(function() {
        $(this).click(function(event) {
            form = $(this).closest('form');
            domain = $(this).closest('.mws-form-row').find(':input:first').val().replace('http://', '');
            do_request_to_enrich(form, domain);
            event.preventDefault();
        });
    });
});