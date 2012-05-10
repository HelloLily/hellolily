/*
 * ClickFocus v1
 * 
 * by Cornelis Poppema
 * 
 * Date: Mon May 7 2012
 * 
 */
(function($) {
    $.fn.clickFocus = (function() {
        this.click(function() {
            // Queue execution to make sure this element will receive focus because
            // other queued events might try to focus an element as well.
            setTimeout(function() {
                elementid = this.data('click-focus');
                elem = document.getElementById(elementid);
                if( elem ) 
                    elem.focus();
            }, 0);
        });
    });
})(jQuery);
    