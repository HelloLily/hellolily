$(document).ready(function() {
    // $('.expected_closing_date.datepicker').datepicker();    
    
    // $.datepicker.noWeekends();
    
    // set focus on name
    // TODO workaround this, both elements with this id are on the full add deal page 
    set_focus('id_name');
    
    // $('#deal-stage').buttonset();
    
    // inner function to protect the scope for currentStage
    (function($) {
        var currentStage = null;
        
        $( '#deal-stage :radio' ).button({
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
                    url: '/ajax/deals/deal/' + $(radio_element).closest('#deal-stage').data('object-id') + '/',
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
                    currentStage = $(event.currentTarget.id);
                });
                // on error
                jqXHR.fail(function() {
                    $.jGrowl(gettext('Stage could not be changed to') + ' ' + $(event.target).text(), {
                        theme: 'info mws-ic-16 ic-error'
                    });
                    // reset selected stage
                    $('#' + currentStage).attr('checked', true);
                    $(radio_element).attr('checked',  false);
                    $('#deal-stage :radio').button('refresh');
                });
                // finally do this
                jqXHR.always(function() {
                    // remove request object
                    jqXHR = null;
                });
            }
            
            // // do this on success
            // var successCallback = function(response, hideLoadingDialog) {
                // if( response.error === true ) {
                    // // Request was successful but the form returned with errors
                    // $.jGrowl(gettext('Stage could not be changed to') + ' ' + $(this).text(), {
                        // theme: 'info mws-ic-16 ic-exclamation'
                    // });
                // } else {
                    // $.jGrowl(gettext('Stage has been changed to') + ' ' + $(this).text(), {
                        // theme: 'info mws-ic-16 ic-accept'
                    // });
                // }
//                 
                // // currentStage = $(this).attr('id'); 
            // };
//             
            // // do this on errors
            // var errorCallback = function() {
                // // Show the error image at the right side of the note
                // $.jGrowl(gettext('Stage could not be changed to') + ' ' + $(this).text(), {
                    // theme: 'info mws-ic-16 ic-exclamation'
                // });
//                 
                // // reset selected stage
                // // $('#' + currentStage)[0].checked = true;
                // // $(this)[0].checked = false;
                // // $('#deal-stage :radio').refresh();
            // };
//             
            // // submit form through AJAX
            // sendForm(container, successCallback, errorCallback);
        });
    
    })($);
});
