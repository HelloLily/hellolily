/* Call focus on an element with given id if found in the DOM */
function set_focus(id) {
   element = document.getElementById(id);
   if(element) {
       element.focus();
       setCaretAtEnd(element);
   }
}
    
// show or hide an input field for the user to input an option manually when the 'other'-option
// has been selected in a select element.
function show_or_hide_other_option(select, page_load) {
    form_index = $(select).attr('id').replace(/[^\d.]/g, '');
    form_prefix = $(select).attr('id').substr(0, $(select).attr('id').indexOf(form_index) - 1);
    select_fieldname = $(select).attr('id').substr($(select).attr('id').lastIndexOf(form_index[form_index.length-1]) + 2);
    
    // show/hide input field
    other_type_input = $(select).closest('.mws-form-cols').find('[id$=-other_' + select_fieldname + ']');
    if( $(select).val() == 'other' ) {
        other_type_input.show();
        if( !page_load ) {
            other_type_input.focus();
        }
    } else {
        other_type_input.hide();
        other_type_input.val('');
    }
    
    $.tabthisbody();
}

function setCaretAtEnd(elem) {
    var range;
    var caretPos = $(elem).val().length
    
    if (elem.createTextRange) {
        range = elem.createTextRange();
        range.move('character', caretPos);
        range.select();
    } else {
        elem.focus();
        if (elem.selectionStart !== undefined) {
            elem.setSelectionRange(caretPos, caretPos);
        }
    }
}

// Calculate width for hidden elements by cloning the original
(function($) {
    $.fn.getHiddenOffsetWidth = function () {
        var hiddenElement = $(this).clone().appendTo('body');
        hiddenElement.show();
        var width = $(hiddenElement).outerWidth();
        $(hiddenElement).remove();
        
        return width;
    };
})(jQuery);

// Calculate width for given text or html
(function($) {
    $.textMetrics = function(html) {
        var h = 0, w = 0;
    
        var div = document.createElement('div');
        document.body.appendChild(div);
        $(div).css({
            position: 'absolute',
            left: -1000,
            top: -1000,
            padding: '0px',
            display: 'none',
            'white-space': 'nowrap'
        });

        $(div).html(html);
        
        // TODO: add support for styles
        // var styles = ['font-size', 'font-style', 'font-weight', 'font-family','line-height', 'text-transform', 'letter-spacing'];
        // $(styles).each(function() {
            // var s = this.toString();
            // $(div).css(s, $(el).css(s));
        // });
    
        h = $(div).outerHeight();
        w = $(div).outerWidth();
    
        $(div).remove();
    
        var ret = {
            height: h,
            width: w
        };

        return ret;
    }
})(jQuery);

// Submit a form on ctrl + enter
function submit_form_on_ctrl_enter(event, form) {
	if (event.keyCode == 13) {
        if (event.ctrlKey) {
            form.submit();
        }
        return false;
    }
}

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
