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

if (typeof String.prototype.startsWith != 'function') {
    String.prototype.startsWith = function(str) {
        return this.substring(0, str.length) === str;
    }
}

if (typeof String.prototype.endsWith != 'function') {
    String.prototype.endsWith = function(str) {
        return this.substring(this.length - str.length, this.length ) === str;
    }
}

/* Format telephone number */
function phone_fmt() {
    var el = $(this);
    var phone = el.val();
    if (phone.match(/[a-z]|[A-Z]/)) {
        // if letters are found, skip formatting: it may not be a phone field after all
        return false;
    }

    phone = phone.replace("(0)","");
    phone = phone.replace(/\s|\(|\-|\)|\.|x|:|\*/g, "");
    phone = phone.replace(/^00/,"+");

    if (phone.length == 0) {
        return false;
    }

    if (!phone.startsWith('+')) {
        if (phone.startsWith('0')) {
          phone = phone.substring(1);
        }
        phone = '+31' + phone;
    }

    el.val(phone);
}

//Selects the account belonging to a contact when a contact is selected.
//Also, when an account is selected, it will reset the selected contact if it does not belong to it.
function change_account(id_contact, id_account) {
    contact_pk = $('#'+id_contact).val();
    if (contact_pk == -1) {
        $('#'+id_contact).select2('data', null);
        $('#'+id_account).select2('data', null);
    } else if (contact_pk) {
        var url = "/contacts/json_works_at/" + contact_pk;
        $.getJSON(url, function(data) {
            if (data.works_at.length) {
                    $('#'+id_account).select2('data', {'id': data.works_at[0]['pk'], 'text': data.works_at[0]['name']});
            } else {
                $('#'+id_account).select2('data', null);
            }
        });
    }
}

function change_contact(id_contact, id_account) {
    contact_pk = $('#'+id_contact).val();
    account_pk = $('#'+id_account).val();
    if (account_pk == -1) {
        $('#'+id_contact).select2('data', null);
        $('#'+id_account).select2('data', null);
    } else if (account_pk && contact_pk) {
        var url = "/contacts/json_works_at/" + contact_pk;
        $.getJSON(url, function(works_at) {
            if (works_at.works_at.length) {
                var account = works_at.works_at[0];
                if (account.pk == account_pk) {
                    return;
                }
            }
            // selected contact does not work anywhere or at selected account, reset it
            $('#'+id_contact).select2('data', null);
        });
    }
}

// go to redirect_url, reload if redirect_url is current and/or if it contains an anchor reference
function redirect_to(redirect_url) {
    var current = window.location.href;
    var index = current.indexOf(redirect_url);

    window.location = redirect_url;
    if(index == current.length - redirect_url.length ||
       redirect_url.indexOf('#') != -1) {
        window.location.reload(true);
    }
}

$(function($) {
    // Format phonenumbers for every phone input field
    $('body').on('blur', 'input[name^="phone"]', function() {phone_fmt.call(this)});

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

        var updateModal = function(current, update) {
            if($(current).find('.modal-header').length && $(update).find('.modal-header').length) {
                $(current).find('.modal-header').html($(update).find('.modal-header').html());
            }
            if($(current).find('.modal-body').length && $(update).find('.modal-body').length) {
                $(current).find('.modal-body').html($(update).find('.modal-body').html());
            }
            if($(current).find('.modal-footer').length && $(update).find('.modal-footer').length) {
                $(current).find('.modal-footer').html($(update).find('.modal-footer').html());
            }

            // prettify checkboxes/radio buttons
            var inputs = $("input[type=checkbox]:not(.toggle), input[type=radio]:not(.toggle, .star)");
            if (inputs.size() > 0) {
                App.initUniform(inputs);
            }
        };

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
                    if(response.clear_serialize) {
                        // clear serialized_form so certain modals don't show a popup when completed
                        $(form).data('serialized_form', '');
                    }
                    if(response.error) {
                        if(response.html) {
                            updateModal($(form), response.html);
                        }
                        // loads notifications if any
                        load_notifications();
                    } else if(response.redirect_url) {
                        redirect_to(response.redirect_url);
                    } else {
                        if(response.html) {
                            updateModal($(form), response.html);
                        } else {
                            // fool the "confirm prevent accidental close" popup from triggering
                            $(form).data('serialized_form', $(form).serialize());

                            $(form).closest('.modal').modal('hide');
                        }
                        // loads notifications if any
                        load_notifications();
                    }
                    // Reset all Select2 options
                    init_select2();
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    $(form).find('[data-async-response]').html(jqXHR.responseText);
                    // loads notifications if any
                    load_notifications();
                    // Reset all Select2 options
                    init_select2();
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

    // submit forms with other elements
    $('[data-form-submit]').click(function(event) {
        $($(this).data('form-selector')).submit();
        event.preventDefault();
    });

    if($.fn.datepicker || $.fn.datetimepicker) {
        $('body').removeClass('modal-open'); // fix bug when inline picker is used in modal
    }

	$('body').on('change', '#id_contact', function() {
		if ($('#id_account').length) {
			change_account('id_contact','id_account');
		}
	}).on('change', '#id_account', function() {
        if ($(this).val() == -1 ) {
            $(this).select2('data', null);
        }
		if ($('#id_contact').length) {
			change_contact('id_contact','id_account');
		}
	}).on('change', '#id_case_quickbutton_contact', function() {
		if ($('#id_case_quickbutton_contact').length) {
			change_account('id_case_quickbutton_contact','id_case_quickbutton_account');
		}
	}).on('change', '#id_case_quickbutton_account', function() {
		if ($('#id_case_quickbutton_contact').length) {
			change_contact('id_case_quickbutton_contact','id_case_quickbutton_account');
		}
	}).on('change', '#id_contact_quickbutton_account', function() {
        if ($(this).val() == -1 ) {
            $(this).select2('data', null);
        }
    });
});
