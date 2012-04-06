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
    select_fieldname = $(select).attr('id').replace(form_prefix + '-' + form_index + '-', '');
    
    // show/hide input field
    other_type_input = $('#' + form_prefix + '-' + form_index + '-other_' + select_fieldname);
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