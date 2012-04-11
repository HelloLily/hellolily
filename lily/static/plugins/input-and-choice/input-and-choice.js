// Input And Choice
// by Cornelis Poppema
//
// inspired by Chosen by Patrick Filler (https://github.com/harvesthq/chosen)

(function($) {
    $(document).ready(function() {
        
        /**
         * Create handlers for adding options to select element which supports multiple options
         * to be selected and support for autocomplete suggestions based on this select element.
         */
        function input_and_choice(wrapper) {
            input = $(wrapper).find('.input-and-choice-input')[0];
            button = $(wrapper).find('.input-and-choice-button')[0];
            select = $(wrapper).find('.input-and-choice-select')[0];
            list = $(wrapper).find('.input-and-choice-list')[0];
            
            // TODO: take width changes into account when parent gets resized
            var gap = $(input).parent().width() - $(input).outerWidth() - $(button).outerWidth();
            if( gap <= 0 ) {
                $(input).width($(input).width() + gap);
                $(input).width($(input).width() - 5);
            }
            $(list).width($(input).outerWidth() + 5 + $(button).outerWidth());
            
            // show pre-selected options
            $(select).find('option:selected').each(function() {
                add_selection(input, select, list, $(this).val(), true);
            });
            
            // detect autocomplete suggestions
            update_autocomplete_suggestions(input, select);    
            
            // add click handler to button
            $(button).click(function(event) {
                value = $(input).val();
                if( value.length ) {
                    add_selection(input, select, list, $.trim(value));
                    // detect autocomplete suggestions
                    update_autocomplete_suggestions(input, select);  
                        
                    // clear text input
                    $(input).val('');
                }
                $(this).blur();
            });
            
            // add keypress handler to input
            $(input).keypress(function(event) {
                if( event.keyCode == $.ui.keyCode.ENTER ) {
                    event.preventDefault();
                    $(button).click();
                }
            });
            
            // add click handlers to anchors in list
            $(list).find('.search-choice-close').live('click', function(event) {
                search_choice = $(event.target).parent();
                remove_selection(select, list, search_choice.text(), search_choice);
            }); 
        }
        
        /**
         * Update autocomplete suggestions for given input based on the options from a select
         * element. Already selected options won't show in the suggestions.
         */
        function update_autocomplete_suggestions(input, select) {
            var suggestions = [];
            
            // add all option elements that are not selected
            $(select).find('option:not(:selected)').each(function() {
                value = $.trim($(this).val());
                text = $.trim($(this).text());
                if( value.length ) {
                    value = text;
                    // save key-value pair
                    suggestions.push({"label:": value, "value": text});
                }
            });
            
            // add selected items to the list with selected items
            $(select).find('option:selected').each(function() {
                add_selection(input, select, list, $.trim($(this).val()));
            });
            
            $(input).autocomplete({
                minLength: 0,
                source: suggestions,
                select: function(e, ui) {
                    add_selection(input, select, list, $.trim(ui.item.value));
                    // detect autocomplete suggestions
                    update_autocomplete_suggestions(input, select);  
                    
                    $(this).autocomplete('search', $(this).val());

                    // prevent selected value as the new value for $(input)
                    $(input).val('');
                    return false;
                },
                open: function(e, ui) {
                    $(this).addClass('no-bottom-radius');
                },
                close: function(e, ui) {
                    $(this).removeClass('no-bottom-radius');
                    $(this).trigger('blur');
                }
            }).focus(function() {
                $(this).autocomplete('search', $(this).val());
            });
        }
        
        /**
         * Select an existing option or add the option if it doesn't.
         */
        function add_selection(input, select, list, value, page_load) {
            option = undefined;
            $(select).find('option').each(function() {
               if( $(this).val().toLowerCase() == value.toLowerCase() ) {
                   // give back the actual element instead of the wrapped jquery object
                   option = $(this)[0];
               } 
            });
            
            if( option == undefined ) {
                // create a new option if none exist with 'value' as value
                $(select).append('<option selected="selected" value="' + value + '" >' + value + '</option>');
            } else {
                // don't add if option is already selected except on page load
                if( option.selected && !page_load ) {
                    return;
                }
                
                // mark existing option as selecting
                $(option).attr('selected', 'selected');
            }
            
            // add selected option visibly
            var item = $('<li>').addClass('search-choice');
            var value = $('<span>').appendTo(item).text(value);  
            var close = $('<a>').addClass('search-choice-close')
                .attr({href: 'javascript:void(0)'})
                .appendTo(item);  
            item.appendTo(list);
            
            // show options-wrapping element if it was hidden
            if( !$(list).is(':visible') ) {
                $(list).show();
            }
        }
        
        /**
         * Deselect option for 'text'. 
         */
        function remove_selection(select, list, text, search_choice) {
            text = $.trim(text);
            
            option = $(select).find('option').filter(function() { return $(this).html() == text})[0];
            if( option != undefined ) {
                // deselect option 
                $(option).removeAttr('selected');
                
                // remove option
                $(search_choice).remove();
            }
            
            // hide options-wrapping element if there are no selected options
            selected = $(list).find('.search-choice');
            if( selected.length == 0 ) {
                $(list).hide();
            }
            
            // update auto suggestions
            update_autocomplete_suggestions(input, select);
        }
        
        $('.input-and-choice').each(function(index, element){
            input_and_choice(element); 
        });
    });
})(jQuery);
