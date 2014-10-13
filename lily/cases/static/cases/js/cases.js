// Handle the status selection.
$(document).ready(function() {
    // inner function to protect the scope for currentStatus
    (function($) {
        var currentStatus = $('input[name=radio]:checked', '#case-status').closest('label').attr('for');
        $('#case-status').click(function(event) {
            var radio_element = $('#' + $(event.target).closest('label').attr('for'));
            if( radio_element.attr('id') != currentStatus ) {
                // try this
                var jqXHR = $.ajax({
                    url: '/cases/update/status/' + $(radio_element).closest('#case-status').data('object-id') + '/',
                    type: 'POST',
                    data: {
                        'status': $(radio_element).val()
                    },
                    beforeSend: addCSRFHeader,
                    dataType: 'json'
                });
                // on success
                jqXHR.done(function(data, status, xhr) {
                    currentStatus = radio_element.attr('id');
                    $('#status').text(data.status);
                    // loads notifications if any
                    load_notifications();
                });
                // on error
                jqXHR.fail(function() {
                    // reset selected status
                    $(radio_element).attr('checked', false);
                    $(radio_element).closest('label').removeClass('active');
                    $('#' + currentStatus).attr('checked', true);
                    $('#' + currentStatus).closest('label').addClass('active');
                    // loads notifications if any
                    load_notifications();
                });
                // finally do this
                jqXHR.always(function() {
                    // remove request object
                    jqXHR = null;
                });
            }
        });
    })($);
});

// Next functions together enable CSRF Tokens being sent with AJAX requests.
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function sameOrigin(url) {
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
function safeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function addCSRFHeader(jqXHR, settings) {
    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        jqXHR.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
}
