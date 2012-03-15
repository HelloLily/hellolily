$(document).ready(function() {
    var error_lists = $('.errorlist');
    if(error_lists.length) {
        var first = error_lists[0];
        var input = jQuery(first).nextAll('input').eq(0);
        input.focus();
    }
})