$(document).ready(function() {

    var check_history_dates = function() {
        var data = $('.object-list-item').last().data('sort-date');
        var hash = parseInt(window.location.hash.substring(1));

        var data_date = new Date(data * 1000); // Django epoch is in seconds instead of milliseconds, so we convert
        var hash_date;

        // Check if the hash is a number, so we can make a date
        if (isNaN(hash) === false) {
            // Hash is a number
            hash_date = new Date(hash * 1000); // Django epoch is in seconds instead of milliseconds, so we convert
        } else {
            // Hash is not a number
            hash_date = new Date(); // We use current datetime
        }
        
        console.log(hash_date);
        console.log(data_date);

        // Check if we need to load more history list items
        if (hash_date < data_date) {
            load_more_history(check_history_dates, true);
        }
    };

    var load_more_history = function(callback, scroll) {
        var last_list_item = $('.object-list-item').last();
        var data = last_list_item.data('sort-date');
        var button = $('.object-list-buttons > button#load-more');
        var loading = $('.object-list-buttons > button#item-loading');
        var url = button.data('url') + '?datetime=' + data;
        var end_of_list_button = $('.object-list-buttons > button#end-of-list');

        // Disable the load more button (show animation or something)
        button.hide();
        loading.show();

        // Make ajax call to load more history list items
        var jqXHR = $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json'
        });

        jqXHR.done(function (response) {
            var html = response.html;

            if (html !== '') {
                $('#history_list').append(html);
                button.show();
            } else {
                button.hide();
                end_of_list_button.show();
            }

            if (response.hide_button === true) {
                button.hide();
                end_of_list_button.show();
            }

            // Put the last date in the url
            window.location.hash = $('.object-list-item').last().data('sort-date');
            
            if (scroll !== undefined) {
                $('html, body').animate({
                    scrollTop: last_list_item.offset().top
                }, 1000);
            }

            if (callback !== undefined) {
                callback();
            }
        });

        jqXHR.fail(function() {
            console.log('faaaiiilll!');
        });

        jqXHR.always(function() {
            loading.hide();
        })
    };

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

    check_history_dates();

});