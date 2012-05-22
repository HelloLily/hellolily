/**
 * Dialog to use when asking to overwrite existing account information.
 */
function dataprovider_ask_overwrite(msg, func) {
    var confirm_dialog = $('<div id="dialog-confirm" title="Overwrite?"><div class="mws-form"><div class="mws-form-inline"><div class="mws-form-row">' + msg + '?</div></div></div></div>');

    $( confirm_dialog ).dialog( "destroy" );

    $( confirm_dialog ).dialog({
        resizable: false,
        modal: true,
        width: 640,
        buttons: [
            {
                'class': 'mws-button red float-left',
                text: gettext('Cancel'),
                click: function() {
                    // cancel form on NO
                    $(this).dialog('close');
                }
            },
            {
                'class': 'mws-button green',
                text: gettext('Overwrite'),
                click: function() {
                    func();
                    $( this ).dialog( "close" );
                }
            }
        ]
    });
}


/**
 * Try filling up a form with data from provided json object
 */
function dataprovider_json_to_form(json, form) {
    // set company name
    if( json.name ) {
        var name = $(form).find('[name="name"]');
        var set_name = function() { $(name).val(json.name); }
        if( $(name).val().length > 0) {
            if( $.trim($(name).val()) != json.name) {
                var result = dataprovider_ask_overwrite('Do you want to overwrite the account\'s name with "' + json.name + '"?', set_name);
            }
        } else {
            set_name();
        }

    }
    // set description
    if( json.description ) {
        var description = $(form).find('[name="description"]');
        if (description.val() !== undefined ){
            var set_description = function() { $(description).val(json.description); link = $(form).find('a.click-show[data-click-show="description_wrapper"]'); link.click(); }
            if( $(description).val().length > 0) {
                if( $.trim($(description).val()) != json.description) {
                    var result = dataprovider_ask_overwrite('Do you want to overwrite the account\'s description with "' + json.description + '"?', set_description);
                }
            } else {
                set_description();
            }
        }
    }
    // add tags
    // if( json.tags.length ) {
    	// input = $(form).find('.input-and-choice-input');
    	// button = $(form).find('.input-and-choice-button');
            // for( var i = 0; i < json.tags.length; i++ ) {
            	// input.val(json.tags[i]);
                // button.click();
                // input.val('');
            // }
    // }
    // add phone numbers
    if( json.phone_numbers.length ) {
        phone_numbers_container = $(form).find('.phone_numbers-add-row').parent();
        popup_phonenumber = $(form).find('[name="phone"]');
        if (phone_numbers_container.length){
            for( var i = 0; i < json.phone_numbers.length; i++ ) {
                $(form).find('.phone_numbers-add-row').click();
                phone_number_elem = $(phone_numbers_container).find('.phone_numbers:visible:last');
                phone_number = json.phone_numbers[i];

                $(phone_number_elem).find('[name^="phone_numbers"][name$="raw_input"]').val(phone_number);
            }
        } else if (popup_phonenumber.length) {
            var set_phonenumber = function() { $(popup_phonenumber).val(json.phone_numbers); }
            if( $(popup_phonenumber).val().length > 0) {
                if( $.trim($(popup_phonenumber).val()) != json.popup_phonenumber) {
                    var result = dataprovider_ask_overwrite('Do you want to overwrite the account\'s phone number with "' + json.phone_numbers[0] + '"?', set_phonenumber);
                }
            } else {
                set_phonenumber();
            }
        }

    }
    // add addresses
    if( json.addresses.length ) {
        addresses_container = $(form).find('.addresses-add-row').parent();
        for( var i = 0; i < json.addresses.length; i++ ) {
        	$(form).find('.addresses-add-row').click();
            address_elem = $(addresses_container).find('.addresses:visible:last');
            address_json = json.addresses[i];

            $(address_elem).find('[name^="addresses"][name$="street"]').val(address_json.street)
            $(address_elem).find('[name^="addresses"][name$="street_number"]').val(address_json.street_number)
            $(address_elem).find('[name^="addresses"][name$="complement"]').val(address_json.complement)
            $(address_elem).find('[name^="addresses"][name$="postal_code"]').val(address_json.postal_code)
            $(address_elem).find('[name^="addresses"][name$="city"]').val(address_json.city)
            $(address_elem).find('[name^="addresses"][name$="country"]').val(address_json.country)
        }
    }
    // set legalentity
    if( json.legalentity )
        $(form).find('[name="legalentity"]').val(json.legalentity);

    // set taxnumber
    if( json.taxnumber )
        $(form).find('[name="taxnumber"]').val(json.taxnumber);

    // set bankaccountnumber
    if( json.bankaccountnumber )
        $(form).find('[name="bankaccountnumber"]').val(json.bankaccountnumber);

    // set cocnumber
    if( json.cocnumber )
        $(form).find('[name="cocnumber"]').val(json.cocnumber);

    // set iban
    if( json.iban )
        $(form).find('[name="iban"]').val(json.iban);

    // set bic
    if( json.bic )
        $(form).find('[name="bic"]').val(json.bic);
}
