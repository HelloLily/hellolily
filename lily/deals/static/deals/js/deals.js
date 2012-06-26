$(document).ready(function() {
	// set focus on name
    set_focus('id_name');
    
    // inner function to protect the scope for currentStage
    (function($) {
        var currentStage = null;
        
        $('#deal-stage :radio').button({
            create: function(event, ui) { 
                if( event.target.checked ) {
                    currentStage = event.target.id;
                }
            }
        });
        
        $('#deal-stage .ui-button').click(function(event) {
            var radio_element = $('#' + $(event.target).closest('label').attr('for'));
            if( radio_element.attr('id') != currentStage ) {            
                // try this
                var jqXHR = $.ajax({
                    url: '/deals/edit/stage/' + $(radio_element).closest('#deal-stage').data('object-id') + '/',
                    type: 'POST',
                    data: {
                        'stage': $(radio_element).val()
                    },
                    beforeSend: addCSRFHeader,
                    dataType: 'json',
                })
                // on success
                jqXHR.done(function(data, status, xhr) {
                    $.jGrowl(gettext('Stage has been changed to') + ' ' + $(event.target).text(), {
                        theme: 'info mws-ic-16 ic-accept'
                    });
                    currentStage = radio_element.attr('id');
                    
                    // check for won/lost and closing date
                    if( data.closed_date ) {
                        $('.closed-date.actual span').text(data.closed_date);
                        $('.closed-date.actual').removeClass('hidden');
                    } else {
                        $('.closed-date.actual span').text('');
                        $('.closed-date.actual:visible').addClass('hidden');
                    }
                });
                // on error
                jqXHR.fail(function() {
                    $.jGrowl(gettext('Stage could not be changed to') + ' ' + $(event.target).text(), {
                        theme: 'info mws-ic-16 ic-error'
                    });
                    // reset selected stage
                    $(radio_element).attr('checked', false);
                    $('#' + currentStage).attr('checked', true);
                    $('#deal-stage :radio').button('refresh');
                });
                // finally do this
                jqXHR.always(function() {
                    // remove request object
                    jqXHR = null;
                });
            }
        });
    
    })($);
});
