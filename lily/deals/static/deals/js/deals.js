// Handle the stage selection.
$(document).ready(function() {
    // inner function to protect the scope for currentStage
    (function($) {
        var currentStage = $('input[name=radio]:checked', '#deal-stage').closest('label').attr('for');
        $('#deal-stage').click(function(event) {
            var radio_element = $('#' + $(event.target).closest('label').attr('for'));
            if( radio_element.attr('id') != currentStage ) {
                // try this
                var jqXHR = $.ajax({
                    url: '/deals/update/stage/' + $(radio_element).closest('#deal-stage').data('object-id') + '/',
                    type: 'POST',
                    data: {
                        'stage': $(radio_element).val()
                    },
                    beforeSend: addCSRFHeader,
                    dataType: 'json',
                });
                // on success
                jqXHR.done(function(data, status, xhr) {
                    currentStage = radio_element.attr('id');
                    $('#status').text(data.stage);
                    // check for won/lost and closing date
                    if( data.closed_date ) {
                        $('#closed-date').text(data.closed_date);
                        $('#closed-date').removeClass('hide');
                        $('#expected-closing-date:visible').addClass('hide');
                    } else {
                        $('#closed-date').text('');
                        $('#closed-date:visible').addClass('hide');
                        $('#expected-closing-date').removeClass('hide');
                    }
                    // loads notifications if any
                    load_notifications();                    
                });
                // on error
                jqXHR.fail(function() {
                    // reset selected stage
                    $(radio_element).attr('checked', false);
                    $(radio_element).closest('label').removeClass('active');
                    $('#' + currentStage).attr('checked', true);
                    $('#' + currentStage).closest('label').addClass('active');
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
