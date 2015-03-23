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

                /*
                $(elem).keydown(function(event) {
                    if(event.keyCode == 9 || $(elem).data('tab-list') == 'yes') { //$.ui.keyCode.TAB
                        $(elem).trigger('blur');
                        $('.tabbable["tabindex"=tabindex+idx+1]).trigger('focus');
                        return false;
                    }
                });
                */

                if(tabthese.length - 1 == idx) {
                    $(elem).attr('data-tab-last', 'yes');
                } else {
                    $(elem).removeAttr('data-tab-last');
                }
            });
            tabindex += tabthese.length;
        });
       }
})(jQuery);
