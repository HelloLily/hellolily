/*
 * TabThis v1.1
 * 
 * by Cornelis Poppema
 * 
 * Date: Mon May 7 2012
 * 
 */
(function($) {
	$.tabthisbody = function() {
    	var tabindex = 1;
	    $('body .tabthis:visible').each(function() {
	        tabthese = $(this).find('.tabbable:visible'); //.not('.tabthis');
	        $(tabthese).each(function(idx, elem) {
	            $(elem).attr('tabindex', tabindex+idx);
	        });
	        tabindex += tabthese.length;
	    });
   	}
})(jQuery);