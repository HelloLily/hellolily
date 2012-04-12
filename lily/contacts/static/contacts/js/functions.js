$(document).ready(function() {
	// TODO: put in utils or something    
    $('input:checkbox').screwDefaultButtons({
        checked:    'url(/static/plugins/screwdefaultbuttons/images/checkbox_checked.png)',
        unchecked:  'url(/static/plugins/screwdefaultbuttons/images/checkbox_unchecked.png)',
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
        formset = $(this).parentsUntil('.mws-form-row', '.mws-formset');
        input_siblings = $(formset).siblings().find('.email_is_primary label input');
        
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
    form_prefices = ['email_addresses', 'phone_numbers'];
    $.each(form_prefices, function(index, form_prefix) {
        $('[class*="' + form_prefix + '"][class$="mws-formset"]').each(function(index, formset) {
            pk = $(formset).attr('class').replace(/[^\d.]/g, '');
            formset_class = form_prefix + '_' + pk;
            
            $(formset).formset( {
                formTemplate: $('#' + formset_class + '-form-template'), // needs to be unique per formset
                prefix: formset_class, // needs to be unique per formset
                addText: gettext('Add another'),
                formCssClass: formset_class, // needs to be unique per formset
                addCssClass: formset_class + '-add-row add-row', // needs to be unique per formset
                deleteCssClass: formset_class + '-delete-row' // needs to be unique per formset
            });
        });
    });
});