$(function() {
    function sanitize_domain(domain) {
        return $.trim(domain.replace('http://', ''));
    }

    function fill_field(input, value) {
        if (typeof value !== 'string') {
            var unique_values = value.concat($(input).val().split(',')).filter(function(val, index, self) {
                return (self.indexOf(val) === index) && (val !== '');
            });
            $(input).val(unique_values.join());
        } else {
            $(input).val(value);
        }
        $(input).change();
    }

    function fill_form(form, data, fields, formsets) {
        var check_overwrite_fields = [];

        // Loop through all fields
        fields.forEach(function(field) {
            // Check if there is data for the field, else do nothing
            if (data[field]) {
                // Input is the field in the current form
                var input = $(form).find('[name="' + field + '"]');
                // Check if the field does not exist in the current form
                if ($(input).val() !== undefined){
                    // Check if the field has a value and that value is not the field placeholder
                    if ($(input).val().length > 0 && $(input).val() !== $(input).attr('placeholder')) {
                        // Field is not empty, check before overwrite
                        check_overwrite_fields.push(field);
                    } else {
                        // Field is empty, fill it with new data
                        fill_field(input, data[field]);
                    }
                }
            }
        });

        // Check if there are fields for which we need to do an overwrite check
        if (check_overwrite_fields.length !== 0) {4
            // Ask the user whether to overwrite or not
            var overwrite = confirm('Do you wish to overwrite the following fields?\n' + check_overwrite_fields.join('\n'));
            // Check what user said
            if (overwrite === true) {
                // Loop through fields that need to be overwritten
                check_overwrite_fields.forEach(function(field) {
                    var input = $(form).find('[name="' + field + '"]');
                    fill_field(input, data[field]);
                });
            }
        }

        // Loop through formsets
        for (var i=0; i < formsets.length; i++) {
            var formset = formsets[i];
            // Check if there is data for the formset
            if (data[formset].length !== 0) {
                var formset_div = $(form).find('#' + formset);
                var formset_add_link = $(formset_div).find('[data-formset-add]');
                var new_formsets = data[formset];
                var found_input;

                for (var j = 0; j < new_formsets.length; j++) {
                    var new_formset = new_formsets[j];
                    var insert_new_formset = false;
                    var new_element;

                    if (typeof new_formset === 'object') {
                        var key;
                        var has_found_input = false;
                        for (key in new_formset) {
                            found_input = $(formset_div).find(':input[name$="' + key +'"]');
                            if (found_input.length !== 0){
                                has_found_input = true;
                                found_input = found_input.filter(function () {
                                    var val = $(this).val();
                                    var new_val = new_formset[key];

                                    return ((val === '' && new_val === null) || val == new_val);
                                });
                                if (found_input.length === 0) {
                                    // One of the values is different so we need to add a new formset
                                    insert_new_formset = true;
                                }
                            }
                        }
                        if (insert_new_formset === true || has_found_input === false) {
                            $(formset_add_link).click();
                            new_element =  $(formset_div).find('[data-formset-body] [data-formset-form]:last');
                            for (key in new_formset) {
                                $(new_element).find(':input[name$="' + key +'"]').val(new_formset[key]);
                            }
                        }
                    } else if (typeof new_formset === 'string') {
                        found_input = $(formset_div).find(':input').filter(function () {
                            return $(this).val() == new_formset;
                        });
                        if (found_input.length === 0) {
                            $(formset_add_link).click();
                            new_element =  $(formset_div).find('[data-formset-body] [data-formset-form]:last');
                            $(new_element).find(':input:first').val(new_formset);
                        }
                    } else {

                    }
                }
            }
        }
    }

    $('body').on('click', ':button.dataprovider', function(event) {
        var button = $(this)
        var form = $(this).closest('form');
        var input = $(this).parents('.dataprovider').find(':input:first');

        var domain = sanitize_domain($(input).val());

        // Show busy gui to user
        $(button).button('loading');
        toastr.info('Beaming up the information now, almost within range!', 'I\'m on my way!');

        var url = '/provide/account/' + domain;
        var jqxhr = $.getJSON(url);

        jqxhr.done(function(data) {
            var fields = [
                'name',
                'description',
                'legalentity',
                'taxnumber',
                'bankaccountnumber',
                'cocnumber',
                'iban',
                'bic',
                'tags',
            ];
            var formsets = [
                'email_addresses',
                'phone_numbers',
                'addresses',
            ];

            fill_form(form, data, fields, formsets);
            toastr.success('We did it! Your new data should be right there waiting for you.', 'Yeah!');
        });

        jqxhr.fail(function(){
            toastr.error('There was an error trying to fetch your data, please don\'t be mad..', 'Oops!');
        });

        jqxhr.always(function() {
            $(button).button('reset');
        });

        event.preventDefault();
    })
});