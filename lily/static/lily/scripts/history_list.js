$(function($) {
    var check_history_dates = function() {
        var sort_date_in_seconds = $('.history-list-item').last().data('sort-date');
        var hash = parseInt(window.location.hash.substring(1), 10);

        // in seconds, convert to milliseconds
        var last_sort_date = new Date(sort_date_in_seconds * 1000);
        var hash_date;

        // check if the hash is a number
        if (isNaN(hash) === false) {
            hash_date = new Date(hash * 1000);
        } else {
            hash_date = new Date();
        }

        // check if we need to load more history list items
        if (hash_date < last_sort_date) {
            show_more_history(check_history_dates, true);
        }
    };

    var show_more_history = function(callback, scroll) {
        $('#history .show-more').button('loading');

        var last_sort_date = $('#history .history-list-item').last().data('sort-date');
        var jqXHR = $.ajax({
            url: $('#history .show-more').data('remote'),
            data: {'datetime': last_sort_date},
            type: 'GET',
            dataType: 'json'
        }).done(function(response) {
            if(response.html) {
                $('#history-list').append(response.html);
            } else if(response.redirect_url) {
                redirect_to(response.redirect_url);
            }

            // put the last date in the url
            window.location.hash = $('#history .history-list-item').last().data('sort-date');

            // change button state
            if(!response.show_more) {
                $('#history .show-more').button('disabled');
                // push to event loop
                setTimeout(function () {
                    $('#history .show-more').attr('disabled', 'disabled');
                }, 0);
            }

            // reset button state
            function reset_show_more() {
                if(response.show_more) {
                    $('#history .show-more').button('reset');
                }
            }
            // reset button after scroll or reset immediately
            if(scroll) {
                $('html, body').animate({
                    scrollTop: $('#history .history-list-item').last().offset().top
                }, 300, reset_show_more);
            } else {
                reset_show_more();
            }

            if(callback) {
                callback();
            }
        });
    };

    // show more history on click
    $('#history .show-more').click(function(e) {
        show_more_history(null, true);
    });

    // attempt to show more history on load if necessary
    check_history_dates();

    $('.object-list-item-options > .emailmessage-view').live('click', function(e) {
        var link = $(this);
        var loading = link.parent().find('.emailmessage-loading');
        var url = link.attr('href');
        var text_div = link.closest('.object-list-item').find('.object-list-item-text');

        link.remove();
        loading.show();

        var jqXHR = $.ajax({
            'url': url,
            'type': 'GET',
            'dataType': 'json'
        });

        jqXHR.done(function(response) {
            text_div.html(response.subject + '<br />' + response.flat_body);
        });

        jqXHR.fail(function(response) {
            console.log('There was an error loading the email message.');
        });

        jqXHR.always(function(response) {
            loading.remove();
        });

        e.preventDefault();
    });

    $('.object-list-buttons > button#load-more').live('click', function(e) {
        load_more_history();
        e.preventDefault();
    });
});
