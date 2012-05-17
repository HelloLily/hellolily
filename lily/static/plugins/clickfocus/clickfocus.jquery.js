/*
 * ClickFocus v1.1
 * 
 * by Cornelis Poppema
 * 
 * Date: Mon May 7 2012
 * 
 */
(function($) {
    $.fn.clickFocus = (function() {
        this.click(function(event) {
            // Queue execution to make sure this element will receive focus because
            // other queued events might try to focus an element as well.
            setTimeout(function() {
                elementid = $(event.target).data('click-focus');
                element = document.getElementById(elementid);
                if( element ) 
                    element.focus();
                    setCaretAtEnd(element);
            }, 0);
        });
    });
    
    /**
     * One-time show-something-click function. Shows an element and removes itself 
     * from the DOM afterwards.
     */
    $.fn.clickShowAndFocus = (function() {
        this.click(function(event) {
            // Queue execution to make sure this element will receive focus because
            // other queued events might try to focus an element as well.
            setTimeout(function() {
                elementid = $(event.target).data('click-show');
                element = document.getElementById(elementid);
                if( element ) {
                	$(event.target).remove();
                	$(element).show();
                	input = $(element).find(':input:visible:first');
                	if( input ) {
                    	input.focus();
                    	setCaretAtEnd(input[0]);
                   	}
                }
            }, 0);
        });
    });
    
    $(document).ready(function() {
	    $('.click-focus').clickFocus();
	    $('.click-show').clickShowAndFocus();
    })
})(jQuery);
    