/* Set caret at end of text in given elem */
function setCaretAtEnd(elem) {
    var range;
    var caretPos = $(elem).val().length

    if (elem.createTextRange) {
        range = elem.createTextRange();
        range.move('character', caretPos);
        range.select();
    } else {
        elem.focus();
        if (elem.selectionStart !== undefined) {
            elem.setSelectionRange(caretPos, caretPos);
        }
    }
}

/* Call focus on an element with given id if found in the DOM */
function set_focus(id) {
   element = document.getElementById(id);
   if(element) {
       element.focus();
       setCaretAtEnd(element);
   }
}

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
        $('body').on('click', '[data-source]', function(event) {
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
                        // loads notifications if any
                        load_notifications();
                    } else if(response.redirect_url) {
                        window.location.replace(response.redirect_url);
                        window.location.reload(true);
                    } else {
                        $(form).closest('.modal').modal('hide');
                        // loads notifications if any
                        load_notifications();
                    }
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    $(form).find('[data-async-response]').html(jqXHR.responseText);
                    // loads notifications if any
                    load_notifications();
                }
            });

            event.preventDefault();
        });
    }

    if(toastr) {
        toastr.options = {
            closeButton: true,
            positionClass: 'toast-bottom-right'
        };
    }

    // update address bar with target
    // - this helps showing the correct tab immediately on page load after
    // trying to post a form but receiving errors for instance
    $('[data-toggle="tab"]').on('shown.bs.tab', function(e) {
        window.location.hash = e.target.hash;
    });
});
