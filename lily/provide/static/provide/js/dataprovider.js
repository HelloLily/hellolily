/** 
 * Try filling up a form with data from provided json object 
 */
function dataprovider_json_to_form(json, form) {
    // set company name
    if( json.name )
        $('form [name="name"]').value(json.name);
    // add tags
    if( json.tags.length )
        // make sure the function is available to prevent js errors
        // if(  ) 
            // for( tag in json.tags ) {
//                 
            // }
    // add description
    if( json.description )
        $('form [name="description"]').value(json.description);
    // add email addresses
    // add phone numbers
    // add websites
    // add addresses
    if( json.addresses )
        $('.addresses-add-row').click();
        addresses_container = $('.addresses');
        for( var i = 0; i < json.addresses.length; i++ ) {
            address_elem = $(addresses_container).find('.address')[i];
            
            address_json = json.addresses[0];
            $(address_elem).find('[name^="addresses"] [name$="street"]').value(address_json.street)
            $(address_elem).find('[name^="addresses"] [name$="street_number"]').value(address_json.street_number)
            $(address_elem).find('[name^="addresses"] [name$="complement"]').value(address_json.complement)
            $(address_elem).find('[name^="addresses"] [name$="postal_code"]').value(address_json.postal_code)
            $(address_elem).find('[name^="addresses"] [name$="city"]').value(address_json.city)
            $(address_elem).find('[name^="addresses"] [name$="country"]').value(address_json.country)
        }
}
