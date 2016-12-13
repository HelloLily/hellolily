(function($, window, document) {
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
            submitButton: 'button[type="submit"]',
            parameterChoices: {},
            variablePreviewButton: '#variable_preview_button',
            customVariablePreviewText: '',
        },

        init: function(config) {
            var self = this;

            // Setup config
            if (typeof config === 'object') {
                $.extend(this.config, config);
            }

            self.initListeners();

            $.get('api/messaging/email/template-variables/', function(data) {
                var i;
                var customVariableName;

                if (!jQuery.isEmptyObject(data.default)) {
                    self.config.parameterChoices = data.default;
                    self.config.parameterChoices['Custom variables'] = {};

                    if (data.custom.length) {
                        for (i = 0; i < data.custom.length; i++) {
                            if (data.custom[i].is_public) {
                                customVariableName = ['custom', data.custom[i].name.toLowerCase(), 'public'].join('.');
                                self.config.parameterChoices['Custom variables'][customVariableName] = {
                                    nameDisplay: data.custom[i].name + ' (public)',
                                    previewValue: data.custom[i].text,
                                };
                            } else {
                                customVariableName = ['custom', data.custom[i].name.toLowerCase()].join('.');
                                self.config.parameterChoices['Custom variables'][customVariableName] = {
                                    nameDisplay: data.custom[i].name,
                                    previewValue: data.custom[i].text,
                                };
                            }
                        }
                    }
                }
            });

            self.updateVariableOptions();
        },

        initListeners: function() {
            var toolbar;

            var self = this;
            var cf = self.config;

            $('body')
            .on('click', cf.insertButton, function(event) {
                var templateVariable = $(cf.templateVariableField).html();

                HLInbox.getEditor().focus();
                HLInbox.getEditor().composer.commands.exec('insertHTML', templateVariable);

                event.preventDefault();
            })
            .on('change', cf.variablesField, function() {
                self.updateVariableOptions();
            })
            .on('click', cf.fileUploadField, function(event) {
                $(cf.bodyFileField).click();
                event.preventDefault();
            })
            .on('change', cf.valuesField, function() {
                self.handleValueChange.call(self, this);
            })
            .on('change', cf.bodyFileField, function() {
                self.handleBodyFileChange.call(self, this);
            })
            .on('click', cf.attachmentDeleteButton, function() {
                var attachmentRow = $(this).closest('.form-group');
                self.toggleMarkDeleted(attachmentRow);
            })
            .on('click', cf.attachmentUndoDeleteButton, function() {
                var attachmentRow = $(this).closest('.form-group');
                self.toggleMarkDeleted(attachmentRow);
            })
            .on('click', cf.submitButton, function(event) {
                self.handleFormSubmit(this, event);
            })
            .on('click', cf.variablePreviewButton, function(event) {
                event.preventDefault();
                swal(cf.customVariablePreviewText).done();
            });

            // Set heading properly after change
            toolbar = $(cf.wysiHtmlToolbar);
            $(toolbar).find('a[data-wysihtml5-command="formatBlock"]').click(function(e) {
                var target = e.target || e.srcElement;
                var el = $(target);
                $(toolbar).find('.current-font').text(el.html());
            });
        },

        updateVariableOptions: function() {
            var self = this;
            var valueSelect = $(this.config.valuesField);
            var category = $(this.config.variablesField).val();

            valueSelect.find('option').not('option[value=""]').remove();
            valueSelect.change();

            if (category !== '') {
                if (category === 'Custom variables') {
                    $.each(self.config.parameterChoices[category], function(parameter, variableValues) {
                        valueSelect.append($('<option>', {
                            value: parameter,
                            text: variableValues.nameDisplay,
                        }));
                    });
                } else {
                    $.each(self.config.parameterChoices[category], function(parameter, label) {
                        valueSelect.append($('<option>', {
                            value: parameter,
                            text: label,
                        }));
                    });
                }
            }
        },

        handleValueChange: function(valuesField) {
            var cf = this.config;

            var templateVariableField = $(cf.templateVariableField);
            var templateVariable = $(valuesField).val();
            var category = $(this.config.variablesField).val();

            if (templateVariable !== '') {
                if (category !== 'Custom variables') {
                    $(cf.variablePreviewButton).hide();

                    templateVariableField.html(cf.openVariable + ' ' + templateVariable + ' ' + cf.closeVariable);
                } else {
                    $(cf.variablePreviewButton).show();

                    this.config.customVariablePreviewText = cf.parameterChoices['Custom variables'][templateVariable].previewValue;

                    templateVariableField.html(cf.openVariable + ' ' + templateVariable + ' ' + cf.closeVariable);
                }
            } else {
                templateVariableField.html('');
            }
        },

        handleBodyFileChange: function(bodyFileField) {
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
                        var fields;

                        if (!response.error && response.form) {
                            fields = ['name', 'subject'];

                            $.each(fields, function(index, field) {
                                if (response.form.hasOwnProperty(field)) {
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
                    },
                });
            }
        },

        toggleMarkDeleted: function(attachmentRow) {
            var rowAttachmentName = attachmentRow.find(this.config.templateAttachmentName);

            if (rowAttachmentName.hasClass('mark-deleted')) {
                rowAttachmentName.removeClass('mark-deleted');
            } else {
                rowAttachmentName.addClass('mark-deleted');
            }
        },

        handleFormSubmit: function(submitButton, event) {
            var $form;

            var $containerDiv = $('<div>');

            event.preventDefault();

            $containerDiv[0].innerHTML = HLInbox.getEditor().getValue();
            // Remove resize div
            $containerDiv.find('#resize-div').remove();

            /**
             * You'd expect HLInbox.getEditor().setValue or $('#id_body_html').html
             * would work to set the value of the textarea.
             * Sadly they don't, which is why .val is used
             */
            $('#' + HLInbox.config.textEditorId).val($containerDiv[0].innerHTML);

            $form = $($(submitButton).closest('form'));

            Metronic.blockUI($('.inbox-content'), false, '');

            $form.submit();
        },
    };
})(jQuery, window, document);

