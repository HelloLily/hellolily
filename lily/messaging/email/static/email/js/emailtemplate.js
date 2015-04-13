(function ($, window, document, undefined) {
    window.HLEmailTemplates = {
        config: {
            insertButton: '#id_insert_button',
            variablesField: '#id_variables',
            fileUploadField: '#body_file_upload',
            valuesField: '#id_values',
            bodyFileField: '#id_body_file',
            templateVariableField: '#id_text_value',
            attachmentDeleteButton: '.email-template-attachments [data-formset-delete-button]',
            attachmentUndoDeleteButton: '.email-template-attachments [data-formset-undo-delete]',
            templateAttachmentName: '.template-attachment-name',
            wysiHtmlToolbar: '#wysihtml5-toolbar',
            submitButton: 'button[type="submit"]'
        },

        init: function (config) {
            var self = this;

            // Setup config
            if (typeof (config === 'object')) {
                $.extend(this.config, config);
            }

            self.initListeners();
            self.updateVariableOptions();
        },

        initListeners: function() {
            var self = this,
                cf = self.config;

            $('body')
                .on('click', cf.insertButton, function (event) {
                    var templateVariable = $(cf.templateVariableField).html();
                    HLInbox.getEditor().focus();
                    HLInbox.getEditor().composer.commands.exec('insertHTML', templateVariable);

                    event.preventDefault();
                })
                .on('change', cf.variablesField, function () {
                    self.updateVariableOptions();
                })
                .on('click', cf.fileUploadField, function (event) {
                    $(cf.bodyFileField).click();
                    event.preventDefault();
                })
                .on('change', cf.valuesField, function () {
                    self.handleValueChange.call(self, this);
                })
                .on('change', cf.bodyFileField, function () {
                    self.handleBodyFileChange.call(self, this);
                })
                .on('click', cf.attachmentDeleteButton, function() {
                    var attachmentRow = $(this).closest('.form-group');
                    self.toggleMarkDeleted(attachmentRow);
                })
                .on('click', cf.attachmentUndoDeleteButton , function() {
                    var attachmentRow = $(this).closest('.form-group');
                    self.toggleMarkDeleted(attachmentRow);
                })
                .on('click', cf.submitButton, function (event) {
                    self.handleFormSubmit(this, event);
                });

            // Set heading properly after change
            var toolbar = $(cf.wysiHtmlToolbar);
            $(toolbar).find('a[data-wysihtml5-command="formatBlock"]').click(function(e) {
                var target = e.target || e.srcElement;
                var el = $(target);
                $(toolbar).find('.current-font').text(el.html());
            });
        },

        updateVariableOptions: function () {
            var valueSelect = $(this.config.valuesField);
            var category = $(this.config.variablesField).val();

            valueSelect.find('option').not('option[value=""]').remove();
            valueSelect.change();

            // TODO: LILY-XXX: Change this to API endpoint
            var parameterChoices = {
                "Contact": {
                    "contact.full_name": "Full name",
                    "contact.work_phone": "Work phone",
                    "contact.last_name": "Last name",
                    "contact.twitter": "Twitter",
                    "contact.mobile_phone": "Mobile phone",
                    "contact.first_name": "First name",
                    "contact.linkedin": "Linkedin",
                    "contact.preposition": "Preposition"
                },
                "User": {
                    "user.full_name": "Full name",
                    "user.first_name": "First name",
                    "user.phone_number": "Phone number",
                    "user.preposition": "Preposition",
                    "user.linkedin": "Linkedin",
                    "user.twitter": "Twitter",
                    "user.current_email_address": "Current email address",
                    "user.last_name": "Last name",
                    "user.user_group": "User group"
                },
                "Account": {
                    "account.work_phone": "Work phone",
                    "account.name": "Name",
                    "account.any_email_address": "Any email address"
                }
            };

            if (category !== '') {
                $.each(parameterChoices[category], function(parameter, label) {
                    valueSelect.append($("<option>", {
                        value: parameter,
                        text: label
                    }));
                });
            }
        },

        handleValueChange: function (valuesField) {
            var templateVariableField = $(this.config.templateVariableField);
            var templateVariable = $(valuesField).val();

            if (templateVariable !== ''){
                templateVariableField.html(this.config.openVariable + ' ' + templateVariable + ' ' + this.config.closeVariable)
            } else {
                templateVariableField.html('');
            }
        },

        handleBodyFileChange: function (bodyFileField) {
            var form = $(bodyFileField).closest('form');
            var uploadedTemplate = form.find(bodyFileField).val();

            if (uploadedTemplate) {
                $(form).ajaxStart(function() {
                    Metronic.blockUI($(form).nextAll('form').eq(0), false, '');
                }).ajaxStop(function() {
                    Metronic.unblockUI($(form).nextAll('form').eq(0));
                }).ajaxSubmit({
                    type: 'post',
                    dataType: 'json',
                    url: this.config.parseEmailTemplateUrl,
                    success: function(response) {
                        if(!response.error && response.form) {
                            var fields = ['name', 'subject'];
                            $.each(fields, function(index, field) {
                                if(response.form.hasOwnProperty(field)) {
                                    $('#id_' + field).val(response.form[field]);
                                }
                            });

                            // Set the html
                            HLInbox.getEditor().setValue(response.form.body_html);
                            HLInbox.getEditor().focus();
                            HLInbox.getEditor().composer.element.blur();
                        }

                        // Loads notifications if any
                        load_notifications();
                    },
                    error: function() {
                        // Loads notifications if any
                        load_notifications();
                    }
                });
            }
        },

        toggleMarkDeleted: function (attachmentRow) {
            var rowAttachmentName = attachmentRow.find(this.config.templateAttachmentName);

            if (rowAttachmentName.hasClass('mark-deleted')) {
                rowAttachmentName.removeClass('mark-deleted');
            }
            else {
                rowAttachmentName.addClass('mark-deleted');
            }
        },

        handleFormSubmit: function (submitButton, event) {
            event.preventDefault();

            // Remove unnecessary html
            var containerDiv = $('<div>')[0];
            containerDiv.innerHTML = HLInbox.getEditor().getValue();
            /**
             * You'd expect HLInbox.getEditor().setValue or $('#id_body_html').html
             * would work to set the value of the textarea.
             * Sadly they don't, which is why .val is used
             */
            $('#id_body_html').val($(containerDiv).find('#body-html-content')[0].innerHTML);

            var $form = $($(submitButton).closest('form'));

            Metronic.blockUI($('.inbox-content'), false, '');

            $form.submit();
        }
    }
})(jQuery, window, document);

