$(document).ready(function() {
    // set focus on first name field
    set_focus('id_first_name');
    
    var error_lists = $('.errorlist');
    if(error_lists.length) {
        var first = error_lists[0];
        var input = jQuery(first).nextAll('input').eq(0);
        input.focus();
    }
})