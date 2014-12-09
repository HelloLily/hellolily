(function ($, window, document, undefined) {
    var editor;

    window.HLInbox = {
        config: {
            accountDeactivatedMessage: 'Your account doesn\'t seem to be active. Please activate your account to view your email.',
            inboxCcInput: '.inbox-compose .mail-to .inbox-cc',
            inboxBccInput: '.inbox-compose .mail-to .inbox-bcc',
            singleMessageSelector: '.inbox-content .view-message',
            templateField: '#id_template',
            mailGroupCheckbox: '.mail-group-checkbox',
            singleInboxCheckbox: '.mail-checkbox:not(.mail-group-checkbox)',
            searchFormSubmit: '.search-form [type="submit"]',
            inboxComposeSubmit: '.inbox-compose [type="submit"]',
            replyButton: '.reply-btn',
            inboxFrame: null,
            tagsAjaxSelector: '.tags-ajax'
        },

        init: function (config) {
            var self = this;

            // Setup config
            if (typeof (config === 'object')) {
                $.extend(this.config, config);
            }

            self.initListeners();
            App.fixContentHeight();
            App.initUniform();
        },

        initListeners: function() {
            var self = this,
                cf = self.config;

            $('body')
                .on('click', cf.inboxCcInput, function() {
                    // Handle compose/reply cc input toggle
                    self.handleAdditionalRecipientsInput('cc');
                })
                .on('click', cf.inboxBccInput, function() {
                    // Handle compose/reply bcc input toggle
                    self.handleAdditionalRecipientsInput('bcc');
                })
                .on('change', cf.templateField, function () {
                    self.changeTemplateField.call(self, this);
                })
                .on('click', cf.singleMessageSelector, function () {
                    self.openMessage.call(self, this);
                })
                .on('change', cf.mailGroupCheckbox, function () {
                    self.toggleGroupCheckbox.call(self, this);
                })
                .on('change', cf.singleInboxCheckbox, function () {
                    // Handle single checkbox toggle
                    $(this).parents('tr').toggleClass('active');

                    self.toggleActionsButton();
                    self.updateBulkIds();
                })
                .on('click', cf.replyButton, function () {
                    // Open links when clicking the reply button
                    $('.inbox-view').hide();
                    $('.inbox-loading').show();
                    HLApp.redirectTo($(this).data('href'));
                })
                .on('click', cf.searchFormSubmit, function () {
                    App.blockUI($('.inbox-content'), false, '');
                    $(this).button('loading');
                })
                .on('click', cf.inboxComposeSubmit, function (event) {
                    self.handleInboxComposeSubmit(this, event);
                })
                .on('change', cf.tags, function () {
                    self.handleTagsAjaxChange(this);
                });


            // Set heading properly after change
            var toolbar = $('#wysihtml5-toolbar');
            $(toolbar).find('a[data-wysihtml5-command="formatBlock"]').click(function(e) {
                var target = e.target || e.srcElement;
                var el = $(target);
                $(toolbar).find('.current-font').text(el.html());
            });

            // autogrow on frame load
            $(cf.inboxFrame).load(self.emailFrameAutogrow());

            // initialize uniform checkboxes
            App.initUniform('.mail-group-checkbox');

            // on load
            self.toggleActionsButton();
            self.updateBulkIds();
        },

        // enable/disable actions button when (no) items are selected
        toggleActionsButton: function () {
            var selected = $('' + $('.mail-group-checkbox').attr('data-set') + ':checked');
            if (selected.length) {
                $('.mail-actions').removeClass('disabled');
                $('.email-list-extra-btn').removeClass('disabled');
            } else {
                $('.mail-actions').addClass('disabled');
                $('.email-list-extra-btn').addClass('disabled');
            }
        },

        // update forms that have actions for selected messages
        updateBulkIds: function () {
            var selected = $('' + $('.mail-group-checkbox').attr('data-set') + ':not(.mail-group-checkbox):checked');
            var selectedIds = [];
            for (var i = 0; i < selected.length; i++) {
                selectedIds.push($(selected[i]).val());
            }

            $('.bulk-ids').val(selectedIds.join(','));
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

            editor.observe('load', function() {
                editor.composer.element.addEventListener('keyup', function() {
                    self.resizeEditor();
                });
            });

            // Set heading properly after change
            var toolbar = $('#wysihtml5-toolbar');
            $(toolbar).find('a[data-wysihtml5-command="formatBlock"]').click(function(e) {
                var target = e.target || e.srcElement;
                var el = $(target);
                $(toolbar).find('.current-font').text(el.html());
            });

            // Not putting this in the initListeners since it's only used in the email compose
            $(window).on('resize', function() {
                self.resizeEditor();
            });
        },

        resizeEditor: function () {
            $('.wysihtml5-sandbox')[0].style.height = editor.composer.element.scrollHeight + 'px';
        },

        handleAdditionalRecipientsInput: function (inputType) {
            var $ccLink = $('.inbox-compose .mail-to .inbox-' + inputType);
            var $inputField = $('.inbox-compose .input-' + inputType);
            $ccLink.hide();
            $inputField.show();
            $('.close', $inputField).click(function () {
                $inputField.hide();
                $ccLink.show();
                $inputField.find('.tags').select2('val', '');
            });
        },

        changeTemplateField: function (templateField) {
            var self = this;
            if (templateList) {
                var value = parseInt($(templateField).val());
                var subjectField = $('#id_subject');
                if (value) {
                    if (templateList[value].subject != '') {
                        subjectField.val(templateList[value].subject);
                    }
                    self.getEditor().setValue(templateList[value].html_part + '<br>' + self.getEditor().getValue());
                    self.resizeEditor();
                } else {
                    subjectField.val('');
                    self.getEditor().setValue('');
                    self.resizeEditor();
                }
            }
        },

        openMessage: function (singleMessageSelector) {
            // Open single email message
            if ($(singleMessageSelector).closest('[data-readable]').data('readable') == 'false') {
                alert(this.config.accountDeactivatedMessage);
            } else {
                $('.inbox-content').hide();
                $('.inbox-loading').show();
                HLApp.redirectTo($(singleMessageSelector).closest('[data-href]').data('href'));
            }
        },

        toggleGroupCheckbox: function (mailGroupCheckbox) {
            var $checkbox = $(mailGroupCheckbox);
            // Handle group checkbox toggle
            var checkboxes = $checkbox.attr('data-set');
            var checked = $checkbox.is(':checked');
            $(checkboxes).each(function () {
                if (checked) {
                    $(this).attr('checked', true);
                    $(this).parents('tr').addClass('active');
                } else {
                    $(this).attr('checked', false);
                    $(this).parents('tr').removeClass('active');
                }
            });

            $.uniform.update(checkboxes);

            this.toggleActionsButton();
            this.updateBulkIds();
        },

        handleInboxComposeSubmit: function (inboxCompose, event) {
            event.preventDefault();

            var button_name = $(inboxCompose).attr('name');
            var form = $(inboxCompose).closest('form');

            // Add button name which is used for certain checks
            $('<input>').attr('type', 'hidden')
                .attr('name', button_name)
                .attr('value', '')
                .appendTo(form);

            if (button_name == 'submit-send') {
                // Validation of fields.
                if (!$('#id_send_to_normal').val() && !$('#id_send_to_cc').val() && !$('#id_send_to_bcc').val()) {
                    $('#modal_no_email_address').modal();
                    event.preventDefault();
                    return;
                }
            } else if (button_name == 'submit-discard') {
                // Discarding email, remove all attachments to prevent unneeded uploading.
                $('[id|=id_attachments]:file').remove();
            }

            // Make sure both buttons of the same name are set to the loading state
            $('button[name="' + button_name + '"]').button('loading');

            // No validation needed, remove attachments to prevent unneeded uploading.
            $('[id|=id_attachments]:file').filter(function () {
                return $(inboxCompose).data('formset-disabled') == true;
            }).remove();

            App.blockUI($('.inbox-content'), false, '');

            // Unexplained bug caused form to freeze when submitting, so make sure form always gets submitted
            $(form).submit();
        },

        handleTagsAjaxChange: function (tagsAjax) {
            // Select2 doesn't remove certain values (values with quotes), so make sure that the value of the field is correct
            var values = [];
            var data = $(tagsAjax).select2('data');

            for(var i=0; i < data.length; i++) {
                var recipient_data = data[i];
                values.push(recipient_data.id);
            }

            $(tagsAjax).val(values.join());
        },

        getEditor: function() {
            return editor;
        }
    }
})(jQuery, window, document);
