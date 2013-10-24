$(function($) {
    if($.fn.modal) {
        // spinner template for bootstrap 3
        $.fn.modal.defaults.spinner = $.fn.modalmanager.defaults.spinner =
            '<div class="loading-spinner" style="width: 200px; margin-left: -100px;">' +
                '<div class="progress progress-striped active">' +
                    '<div class="progress-bar" style="width: 100%;"></div>' +
                '</div>' +
            '</div>';

        $.fn.modalmanager.defaults.resize = true;

        // remove any results from other modals
        $('body').on('hidden.bs.modal', '.modal', function() {
            $(this).find('[data-async-response]').html('');
        });

        // remove focus from element that triggered modal
        $('body').on('hide.bs.modal', '.modal', function() {
            $(':focus').blur();
        });

        // open modal with remote content
        $('[data-source]').on('click', function(event) {
            var button = $(this);
            var modal = $($(button).data('target'));

            // create the backdrop and wait for next modal to be triggered
            $('body').modalmanager('loading');

            setTimeout(function() {
                modal.load($(button).data('source'), '', function() {
                    modal.modal();
                });
            }, 300);

            event.preventDefault();
        });

        // ajax submit
        $('body').on('submit', 'form[data-async]', function(event) {
            var form = $(this);
            $(form).ajaxStart(function() {
                $(form).find('[type="submit"]').button('loading');
            }).ajaxStop(function() {
                setTimeout(function() {
                    $(form).find('[type="submit"]').button('reset');
                }, 300);
            }).ajaxSubmit({
                success: function(response) {
                    if(response.error) {
                        if(response.html) {
                            $(form).find('.modal-body').html($(response.html).find('.modal-body').html());
                        }
                    } else if(response.redirect_url) {
                        window.location.replace(response.redirect_url);
                    } else {
                        $(form).closest('.modal').modal('hide');
                    }
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    $(form).find('[data-async-response]').html(jqXHR.responseText);
                }
            });

            event.preventDefault();
        });
    }
});
