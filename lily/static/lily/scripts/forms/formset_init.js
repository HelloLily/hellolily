$(document).ready(function() {
    // enable js formsets on all the following formsets
    form_prefices = {
        'websites': gettext('Add a website'),
        'email_addresses': gettext('Add an e-mail address'),
        'phone_numbers': gettext('Add a phone number'),
        'addresses': gettext('Add an address'),
        'attachments': gettext('Add an attachment')
    };
    for(var form_prefix in form_prefices) {
        var formset_identifier = form_prefix + '-formset';
        var formset_element = $('.' + formset_identifier).not('.formsetted');
        if( formset_element.length ) {
            $(formset_element).formset( {
                formTemplate: $('#' + form_prefix + '-form-template'), // needs to be unique per formset
                prefix: form_prefix, // needs to be unique per formset
                addText: form_prefices[form_prefix],
                formCssClass: formset_identifier, // needs to be unique per formset
                addCssClass: form_prefix + '-add-row', // needs to be unique per formset
                added: function(row) {
                    $.tabthisbody();
                },
                deleteCssClass: form_prefix + '-delete-row', // needs to be unique per formset
            });
            $('.' + formset_identifier).addClass('formsetted');
        }
    }
});
