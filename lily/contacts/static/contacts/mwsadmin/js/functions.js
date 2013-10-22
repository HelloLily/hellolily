$(document).ready(function() {
	// TODO: put in utils or something
    $('input:checkbox').screwDefaultButtons({
        checked:    'url(' + media_url('mwsadmin/plugins/screwdefaultbuttons/images/checkbox_checked.png') + ')',
        unchecked:  'url(' + media_url('mwsadmin/plugins/screwdefaultbuttons/images/checkbox_unchecked.png') + ')',
        width:      16,
        height:     16
    });

    // manually add hover classes when hovering over a label element
    $('.email_is_primary label span').live({
        mouseenter: function() {
            $(this).addClass('state-hover');
        },
        mouseleave: function() {
            $(this).removeClass('state-hover');
        }
    });

    // change selected primary e-mailadres
    $('.email_is_primary label span').live('click', function() {
        // find elements
        formset = $(this).closest('.mws-form-row');
        input_siblings = $(formset).find('.email_is_primary label input');

        // uncheck others
        $(input_siblings).siblings('span').removeClass('checked');

        // check this one
        $(this).addClass('checked');
    })

    // show or hide 'other'-options on page load or when the value changes
    $('select.other:visible').each(function() {
        show_or_hide_other_option($(this)[0], true);
    }).live('change', function() {
        show_or_hide_other_option($(this)[0]);
    });

    // enable formsets for email addresses and phone numbers
    form_prefices = {'email_addresses': gettext('Add an e-mail address'), 'phone_numbers': gettext('Add a phone number')};
    formset_classes = {};

    // find all formset classes
   for(form_prefix in form_prefices) {
        $('[class*="' + form_prefix + '"][class$="mws-formset"]').each(function(index, formset) {
            pk = $(formset).attr('class').replace(/[^\d.]/g, '');
            formset_prefix = form_prefix + '_' + pk;
            formset_class = formset_prefix;

            // only remember formset_class once
            formset_classes[formset_class] = form_prefices[form_prefix];
        });
    };

    // only apply formset() once on each of the found formsets
    for(formset_class in formset_classes) {
        $('.' + formset_class + '-mws-formset').formset( {
            formTemplate: $('#' + formset_class + '-form-template'), // needs to be unique per formset
            prefix: formset_class, // needs to be unique per formset
            addText: formset_classes[formset_class],
            formCssClass: formset_class, // needs to be unique per formset
            addCssClass: formset_class + '-add-row', // needs to be unique per formset
            deleteCssClass: formset_class + '-delete-row', // needs to be unique per formset
            notEmptyFormSetAddCssClass: 'mws-form-item'
        })
    };

});
