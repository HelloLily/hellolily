$(function($) {

    var historyListItems = $('#history-list .history-list-item');

    var check_history_dates = function() {
        var sort_date_in_seconds = $(historyListItems).last().data('sort-date');
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

    var showMoreButton = $('#tab-history .show-more');

    // show more history on click
    $(showMoreButton).click(function() {
        show_more_history(null, true);
    });

    var show_more_history = function(callback, scroll) {
        $(showMoreButton).button('loading');

        var last_sort_date = $(historyListItems).last().data('sort-date');
        var jqXHR = $.ajax({
            url: $(showMoreButton).data('remote'),
            data: {'datetime': last_sort_date},
            type: 'GET',
            dataType: 'json'
        });

        jqXHR.done(function(response) {
            if(response.html) {
                $('#history-list').append(response.html);
            } else if(response.redirect_url) {
                redirect_to(response.redirect_url);
            }
            // put the last date in the url
            window.location.hash = $(historyListItems).last().data('sort-date');

            // change button state
            if(!response.show_more) {
                $(showMoreButton).button('disabled');
                // push to event loop
                setTimeout(function () {
                    $(showMoreButton).attr('disabled', 'disabled');
                }, 0);
            }

            // reset button state
            function reset_show_more() {
                if(response.show_more) {
                    $(showMoreButton).button('reset');
                }
            }
            // reset button after scroll or reset immediately
            if(scroll) {
                $('html, body').animate({
                    scrollTop: $(historyListItems).last().offset().top
                }, 300, reset_show_more);
            } else {
                reset_show_more();
            }

            if(callback) {
                callback();
            }
        });
    };

    // attempt to show more history on load if necessary
    check_history_dates();
});
