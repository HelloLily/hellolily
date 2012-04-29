/* Call focus on an element with given id if found in the DOM */
function set_focus(id) {
   element = document.getElementById(id);
   if(element) {
       element.focus();
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

// Calculate width for given element
(function($) {
    $.textMetrics = function(el) {
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
    
        $(div).html($(el).html());
        $(div).html(el);
        var styles = ['font-size','font-style', 'font-weight', 'font-family','line-height', 'text-transform', 'letter-spacing'];
        $(styles).each(function() {
            var s = this.toString();
            $(div).css(s, $(el).css(s));
        });
    
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
