/* Set caret at end of text in given elem */
function setCaretAtEnd(elem) {
    var range;
    var caretPos = $(elem).val().length;

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

(function($, window, document, undefined){
    var truncatedFields;

    window.HLApp = {
        config: {
            phoneInputFields: 'input[name^="phone"]',
            countryPrefix: '+31',
            truncateFields: '.truncate',
            truncateToken: '&nbsp;(&hellip;)',
            toastrPosition: 'toast-bottom-right',
            contactField: '#id_contact',
            quickContactField: '#id_case_quickbutton_contact',
            accountField: '#id_account',
            quickAccountField: '#id_case_quickbutton_account',
            archiveField: '#id_is_archived',
            archiveButton: '#archive-button',
            saveArchiveText: 'Save and archive',
            saveUnArchiveText: 'Save and unarchive'
        },

        init: function(config) {
            // Setup config
            var self = this;
            if ($.isPlainObject(config)) {
                $.extend(self.config, config);
            }

            self.initListeners();
            self.resetTruncateFields();
            self.initToastr();
            self.initDatePicker();
            self.initModalSpinner();
            self.initArchiveButton();
        },

        initListeners: function() {
            var self = this,
                cf = self.config;
            $('body')
                .on('blur', cf.phoneInputFields, function() {
                    // Format phonenumbers for every phone input field
                    self.formatPhoneNumber.call(self, this);
                })
                .on('change', cf.contactField, function() {
                    self.changedContact(cf.contactField, cf.accountField);
                })
                .on('change', cf.quickContactField, function() {
                    self.changedContact(cf.quickContactField, cf.quickAccountField);
                })
                .on('change', cf.accountField, function() {
                    self.changedAccount(cf.contactField, cf.accountField);
                })
                .on('change', cf.quickAccountField, function() {
                    self.changedAccount(cf.quickContactField, cf.quickAccountField);
                })
                .on('hidden.bs.modal', '.modal', function() {
                    // remove any results from other modals
                    $(this).find('[data-async-response]').html('');
                })
                .on('hide.bs.modal', '.modal', function() {
                    // remove focus from element that triggered modal
                    $(':focus').blur();
                })
                .on('click', '[data-source]', function(event) {
                    self.openModalWithRemoteContent.call(this, event);
                })
                .on('submit', 'form[data-async]', function(event) {
                    self.submitAjaxForm.call(self, this, event);
                })
                .on('shown.bs.tab', '[data-toggle="tab"]', function(e) {
                    // update address bar with target
                    // - this helps showing the correct tab immediately on page load after
                    // trying to post a form but receiving errors for instance
                    window.location.hash = e.target.hash;
                })
                .on('click', cf.archiveButton, function(event) {
                    self.switchArchivedForm.call(self, event);
                });

            $(window).on('resize', function() {
                self.truncateFields();
            });

            // submit forms with other elements
            $('[data-form-submit]').on('click', function(event) {
                $($(this).data('form-selector')).submit();
                event.preventDefault();
            });
        },

        formatPhoneNumber: function(phoneNumberInput) {
            // Format telephone number
            var $phoneNumberInput = $(phoneNumberInput);
            var phone = $phoneNumberInput.val();
            if (phone.match(/[a-z]|[A-Z]/)) {
                // if letters are found, skip formatting: it may not be a phone field after all
                return false;
            }

            phone = phone
                .replace("(0)","")
                .replace(/\s|\(|\-|\)|\.|x|:|\*/g, "")
                .replace(/^00/,"+");

            if (phone.length == 0) {
                return false;
            }

            if (!phone.startsWith('+')) {
                if (phone.startsWith('0')) {
                    phone = phone.substring(1);
                }
                phone = this.config.countryPrefix + phone;
            }

            if (phone.startsWith('+310')) {
                phone = '+31' + phone.substring(4);
            }
            $phoneNumberInput.val(phone);
        },

        setupTruncate: function() {
            truncatedFields = $(this.config.truncateFields);
        },

        truncateFields: function() {
            truncatedFields.truncate({
                token: this.config.truncateToken
            });
        },

        resetTruncateFields: function() {
            this.setupTruncate();
            this.truncateFields();
        },

        initToastr: function() {
            toastr.options = {
                closeButton: true,
                positionClass: this.config.toastrPosition
            };
        },

        initDatePicker: function() {
            $('body').removeClass('modal-open'); // fix bug when inline picker is used in modal
        },

        // Selects the Account belonging to a Contact when a Contact is selected.
        changedContact: function(idContact, idAccount) {
            var $contact = $(idContact),
                $account = $(idAccount),
                contactPk = $contact.val(),
                accountPk = $account.val();
            // Resets the Contact & Accounts if Contact clear is selected.
            if (contactPk == -1) {
                $contact.select2('data', null);
                $account.select2('data', null);
            } else if (contactPk && !accountPk) {
                // Contact is selected, and no Account is selected.
                var url = this.config.contactJsonUrl + contactPk;
                $.getJSON(url, function(data) {
                    if (data.hits.length) {
                        $account.select2('data', {'id': data.hits[0].id, 'text': data.hits[0].name});
                    } else {
                        $account.select2('data', null);
                    }
                });
            }
        },

        // Resets the Contact & Accounts if Account clear is selected.
        changedAccount: function(idContact, idAccount) {
            var $account = $(idAccount);
            if ($account.val() == -1) {
                $(idContact).select2('data', null);
                $account.select2('data', null);
            }
        },

        initModalSpinner: function() {
            // spinner template for bootstrap 3
            $.fn.modal.defaults.spinner = $.fn.modalmanager.defaults.spinner =
                '<div class="loading-spinner" style="width: 200px; margin-left: -100px;">' +
                '<div class="progress progress-striped active">' +
                '<div class="progress-bar" style="width: 100%;"></div>' +
                '</div>' +
                '</div>';

            $.fn.modalmanager.defaults.resize = true;
        },

        openModalWithRemoteContent: function(event) {
            var $button = $(this);
            var modal = $($button.data('target'));

            // create the backdrop and wait for next modal to be triggered
            $('body').modalmanager('loading');

            setTimeout(function() {
                modal.load($button.data('source'), '', function() {
                    modal.modal();
                });
            }, 300);

            event.preventDefault();
        },

        updateModal: function(current, update) {
            var $current = $(current);
            var $update = $(update);
            if($current.find('.modal-header').length && $update.find('.modal-header').length) {
                $current.find('.modal-header').html($update.find('.modal-header').html());
            }
            if($current.find('.modal-body').length && $update.find('.modal-body').length) {
                $current.find('.modal-body').html($update.find('.modal-body').html());
            }
            if($current.find('.modal-footer').length && $update.find('.modal-footer').length) {
                $current.find('.modal-footer').html($update.find('.modal-footer').html());
            }

            // prettify checkboxes/radio buttons
            var inputs = $("input[type=checkbox]:not(.toggle), input[type=radio]:not(.toggle, .star)");
            if (inputs.size() > 0) {
                App.initUniform(inputs);
            }
        },

        submitAjaxForm: function(form, event) {
            var self = this;
            var $form = $(form);
            $form.ajaxStart(function() {
                $form.find('[type="submit"]').button('loading');
            }).ajaxStop(function() {
                setTimeout(function() {
                    $form.find('[type="submit"]').button('reset');
                }, 300);
            }).ajaxSubmit({
                success: function(response) {
                    if(response.clear_serialize) {
                        // clear serialized_form so certain modals don't show a popup when completed
                        $form.data('serialized_form', '');
                    }
                    if(response.error) {
                        if(response.html) {
                            self.updateModal($form, response.html);
                        }
                        // loads notifications if any
                        load_notifications();
                    } else if(response.redirect_url) {
                        location.reload(true);
                    } else {
                        if(response.html) {
                            self.updateModal($form, response.html);
                        } else {
                            // fool the "confirm prevent accidental close" popup from triggering
                            $form.data('serialized_form', $form.serialize());

                            $form.closest('.modal').modal('hide');
                        }
                        // loads notifications if any
                        load_notifications();
                    }
                    // Reset all Select2 options
                    HLSelect2.setupSelect2();
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    $form.find('[data-async-response]').html(jqXHR.responseText);
                    // loads notifications if any
                    load_notifications();
                    // Reset all Select2 options
                    HLSelect2.setupSelect2();
                }
            });
            event.preventDefault();
        },

        redirectTo: function(redirectUrl) {
            // go to redirectUrl, reload if redirectUrl is current
            // and/or if it contains an anchor reference
            var current = window.location.href;
            var index = current.indexOf(redirectUrl);

            window.location = redirectUrl;
            if(index == current.length - redirectUrl.length ||
                redirectUrl.indexOf('#') != -1) {
                window.location.reload(true);
            }
        },

        getCookie: function(name) {
            var value = "; " + document.cookie;
            var parts = value.split("; " + name + "=");
            if (parts.length == 2) return parts.pop().split(";").shift();
        },

        isSameOrigin: function(url) {
            // url could be relative or scheme relative or absolute
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                !(/^(\/\/|http:|https:).*/.test(url));
        },

        safeMethod: function(method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        },

        addCSRFHeader: function(jqXHR, settings) {
            if (!HLApp.safeMethod(settings.type) && HLApp.isSameOrigin(settings.url)) {
                jqXHR.setRequestHeader('X-CSRFToken', HLApp.getCookie('csrftoken'));
            }
        },

        getUrlParameter: function(sParam) {
            var sPageURL = window.location.search.substring(1);
            var sURLVariables = sPageURL.split('&');
            for (var i = 0; i < sURLVariables.length; i++)
            {
                var sParameterName = sURLVariables[i].split('=');
                if (sParameterName[0] == sParam)
                {
                    return decodeURIComponent(sParameterName[1]);
                }
            }
        },

        initArchiveButton: function() {
            var self = this,
                cf = self.config,
                $button = $(cf.archiveButton),
                $archiveField = $(cf.archiveField);
            if ($archiveField.val() === 'True') {
                $button.find('span').text(cf.saveUnArchiveText);
            } else {
                $button.find('span').text(cf.saveArchiveText);
            }
        },

        switchArchivedForm: function(event) {
            var self = this,
                cf = self.config,
                $button = $(cf.archiveButton),
                $archiveField = $(cf.archiveField),
                $form = $($button.closest('form').get(0));
            var archive = ($archiveField.val() === 'True' ? 'False' : 'True');
            $archiveField.val(archive);
            $button.button('loading');
            $form.find(':submit').click();
            event.preventDefault();
        }
    }
})(jQuery, window, document);
