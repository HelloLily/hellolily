/** 
 * Try filling up a form with data from provided json object 
 */
function dataprovider_json_to_form(json, form) {
    // set company name
    if( json.name )
        $(form).find('[name="name"]').val(json.name);
    // set description
    if( json.description ) {
        $(form).find('[name="description"]').val(json.description)
    	// textarea = $(form).find('[name="description"]');
        // textarea.val(json.description);
        // textarea.scrollTop(textarea[0].scrollHeight - textarea.height()).trigger('change');
    }
    // add tags
    if( json.tags.length ) {
    	input = $(form).find('.input-and-choice-input');
    	button = $(form).find('.input-and-choice-button');
            for( var i = 0; i < json.tags.length; i++ ) {
            	input.val(json.tags[i]);
                button.click();
                input.val('');
            }
    }
    // add email addresses
    if( json.email_addresses.length ) {
        email_addresses_container = $(form).find('.email_addresses-add-row').parent();
        for( var i = 0; i < json.email_addresses.length; i++ ) {
        	$(form).find('.email_addresses-add-row').click();
            email_address_elem = $(email_addresses_container).find('.email_addresses:visible:last');
            email_address = json.email_addresses[i];
            
            $(email_address_elem).find('[name^="email_addresses"][name$="email_address"]').val(email_address);
        }
    }
    // add phone numbers
    if( json.phone_numbers.length ) {
        phone_numbers_container = $(form).find('.phone_numbers-add-row').parent();
        for( var i = 0; i < json.phone_numbers.length; i++ ) {
        	$(form).find('.phone_numbers-add-row').click();
            phone_number_elem = $(phone_numbers_container).find('.phone_numbers:visible:last');
            phone_number = json.phone_numbers[i];
            
            $(phone_number_elem).find('[name^="phone_numbers"][name$="raw_input"]').val(phone_number);
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
    // TODO: set cocnumber
}
