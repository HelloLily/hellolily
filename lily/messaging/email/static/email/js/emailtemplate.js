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
            wysiHtmlToolbar: '#wysihtml5-toolbar'
        },

        init: function (config) {
            var self = this;

            // Setup config
            if (typeof (config === 'object')) {
                $.extend(this.config, config);
            }

            self.initListeners();
            self.updateVariableOptions();
            App.fixContentHeight();
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
                });

            // Set heading properly after change
            var toolbar = $(cf.wysiHtmlToolbar);
            $(toolbar).find('a[data-wysihtml5-command="formatBlock"]').click(function(e) {
                var target = e.target || e.srcElement;
                var el = $(target);
                $(toolbar).find('.current-font').text(el.html());
            });

            // initialize uniform checkboxes
            App.initUniform('.mail-group-checkbox');
        },

        updateVariableOptions: function () {
            var valueSelect = $(this.config.valuesField);
            var category = $(this.config.variablesField).val();

            valueSelect.find('option').not('option[value=""]').remove();
            valueSelect.change();

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
                    App.blockUI($(form).nextAll('form').eq(0), false, '');
                }).ajaxStop(function() {
                    App.unblockUI($(form).nextAll('form').eq(0));
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
        }
    }
})(jQuery, window, document);

