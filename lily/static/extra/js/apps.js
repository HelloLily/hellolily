$(document).ready(function() {
    // enable js formsets on all the following formsets 
    form_prefices = {'websites': gettext('Add a website'), 'email_addresses': gettext('Add an e-mail address'), 'phone_numbers': gettext('Add a phone number'), 'addresses': gettext('Add an address')};
    for(form_prefix in form_prefices) {
        formset_element = $('.' + form_prefix + '-mws-formset').not('.formsetted');
        if( formset_element.length ) {
            $(formset_element).formset( {
                formTemplate: $('#' + form_prefix + '-form-template'), // needs to be unique per formset
                prefix: form_prefix, // needs to be unique per formset
                addText: form_prefices[form_prefix],
                formCssClass: form_prefix, // needs to be unique per formset
                addCssClass: form_prefix + '-add-row', // needs to be unique per formset
                added: function(row) { $.tabthisbody(); enableChosen(row); },
                deleteCssClass: form_prefix + '-delete-row', // needs to be unique per formset
                notEmptyFormSetAddCssClass: 'mws-form-item',
            });
            $('.' + form_prefix + '-mws-formset').addClass('formsetted');
        }
    };
    
    // show or hide 'other'-options on page load or when the value changes
    // TODO: fix this
    // $('select.other:visible').each(function() {
        // show_or_hide_other_option($(this)[0], true);
    // }).live('change', function() {
        // show_or_hide_other_option($(this)[0]);
    // });
    
});
