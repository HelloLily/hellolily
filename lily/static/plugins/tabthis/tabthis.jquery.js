/*
 * TabThis v1
 * 
 * by Cornelis Poppema
 * 
 * Date: Mon May 7 2012
 * 
 */
(function($) {
    var tabindex = 1;
    $('.tabthis:visible').each(function() {
        tabthese = $(this).find('.tabbable:visible');
        $(tabthese).each(function(idx, elem) {
            $(elem).attr('tabindex', tabindex+idx);
        });
        tabindex += tabthese.length;
    });
})(jQuery);