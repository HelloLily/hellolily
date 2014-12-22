(function ($, window, document, undefined) {
    window.HLEmailTemplates = {
        config: {
            insertButton: '#id_insert_button',
            variablesField: '#id_variables',
            fileUploadField: '#body_file_upload',
            valuesField: '#id_values',
            bodyFileField: '#id_body_file',
            templateVariableField: '#id_text_value'
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
                });

            // Set heading properly after change
            var toolbar = $('#wysihtml5-toolbar');
            $(toolbar).find('a[data-wysihtml5-command="formatBlock"]').click(function(e) {
                var target = e.target || e.srcElement;
                var el = $(target);
                $(toolbar).find('.current-font').text(el.html());
            });

            // autogrow on frame load
            $(cf.inboxFrame).load(HLInbox.emailFrameAutogrow());

            // initialize uniform checkboxes
            App.initUniform('.mail-group-checkbox');
        },

        updateVariableOptions: function () {
            var valueSelect = $(this.config.valuesField);
            var category = $(this.config.variablesField).val();

            valueSelect.find('option').not('option[value=""]').remove();
            valueSelect.change();
            // initialize uniform checkboxes
            App.initUniform('.mail-group-checkbox');
        },

        emailFrameAutogrow: function () {
            var cf = this.config;

            setTimeout(function () {
                $('.inbox-loading').hide();
                $('.inbox-view').show();
                App.fixContentHeight();

                // highlight selected messages
                $('.mail-checkbox:not(.mail-group-checkbox)').change(function () {
                    $(this).parents('tr').toggleClass('active');
                });

                // do this after .inbox-view is visible
                var ifDoc, ifRef = cf.inboxFrame;

                // set ifDoc to 'document' from frame
                try {
                    ifDoc = ifRef.contentWindow.document.documentElement;
                } catch (e1) {
                    try {
                        ifDoc = ifRef.contentDocument.documentElement;
                    } catch (e2) {
                    }
                }

                // calculate and set max height for frame
                if (ifDoc) {
                    var subtractHeights = [
                        $(cf.inboxFrame).offset().top,
                        $('.footer').outerHeight()
                    ];

                    var maxHeight = $('body').outerHeight();
                    for (var height in subtractHeights) {
                        maxHeight = maxHeight - height;
                    }

                    if (ifDoc.scrollHeight > maxHeight) {
                        ifRef.height = maxHeight;
                    } else {
                        ifRef.height = ifDoc.scrollHeight;
                    }
                }
            }, 300);
        },

        customParser: function () {
            function parse(elementOrHtml, rules, context, cleanUp) {
                return elementOrHtml;
            }

            return parse;
        },

        initWysihtml5: function () {
            var self = this;

            editor = new wysihtml5.Editor('id_body_html', {
                toolbar: 'wysihtml5-toolbar',
                parser: self.customParser(),
                handleTables: false
            });

            editor.observe('load', function () {
                editor.focus();
            });

            // Set heading properly after change
            var toolbar = $('#wysihtml5-toolbar');
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
        }
    }
})(jQuery, window, document);

