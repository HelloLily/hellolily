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
            tagsAjaxSelector: '.tags-ajax',
            emailAccountInput: '#id_send_from',
            sendToNormalField: '#id_send_to_normal',
            overwriteTemplateConfirm: 'Selecting a different template will overwrite the text you\'ve typed. Do you want to load the template anyway?'
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
                    self.changeTemplateField.call(self, this, true);
                })
                .on('change', cf.sendToNormalField, function () {
                    self.changeTemplateField.call(self, cf.templateField, false);
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

        initEmailCompose: function (emailComposeConfig) {
            var self = this;

            if (typeof (emailComposeConfig === 'object')) {
                $.extend(this.config, emailComposeConfig);
            }

            self.initWysihtml5();
            self.loadDefaultEmailTemplate();
        },

        initWysihtml5: function () {
            var self = this;

            editor = new wysihtml5.Editor('id_body_html', {
                toolbar: 'wysihtml5-toolbar',
                parser: self.customParser(),
                handleTables: false
            });

            editor.observe('load', function() {
                editor.focus();
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

        changeTemplateField: function (templateField, templateChanged) {
            var self = this;
            if (templateList) {
                var value = parseInt($(templateField).val());
                var subjectField = $('#id_subject');
                var subject = '';
                var htmlPart = '';
                var recipientId = null;

                if (value) {
                    subject = templateList[value].subject;

                    var messageType = this.config.messageType;

                    if (messageType === 'new' && subject != '') {
                        // Only overwrite the subject if a new email is being created
                        subjectField.val(subject);
                    }

                    var recipient = $('#id_send_to_normal').select2('data')[0];

                    if (typeof recipient !== 'undefined' && typeof recipient.object_id !== 'undefined') {
                        // Check if a contact has been entered
                        recipientId = recipient.object_id;
                    }
                    else if (self.config.fromContact !== '' && self.config.fromContact != null) {
                        // If it's a reply there might be contact set
                        recipientId = self.config.fromContact;
                        self.config.fromContact = null;
                    }

                    // Always get a template
                    var url = self.config.getTemplateUrl + value;

                    if (recipientId != null) {
                        // If a recipient has been set we can fill extra variables
                        url += '?contact_id=' + recipientId;
                    }

                    $.getJSON(url, function (data) {
                        htmlPart = data['template'];
                        self.setNewEditorValue(htmlPart, templateChanged);
                    });
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

            // Make sure replies on this email don't break the application
            editor.setValue(editor.getValue().replace(' id="compose-email-template"', ''));

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
        },

        loadDefaultEmailTemplate: function() {
            var self = this;
            var emailAccountId = $(self.config.emailAccountInput).val();
            var url = self.config.defaultEmailTemplateUrl + emailAccountId;

            $.getJSON(url, function(data) {
                $(self.config.templateField).select2('val', data['template_id']).trigger('change');
            });
        },

        setNewEditorValue: function (htmlPart, templateChanged) {
            // getValue returns a string, so convert to elements
            var editorValue = $(editor.getValue());
            var currentTemplate = editorValue.closest('#compose-email-template');
            var newEditorValue = '';

            // Check if an email template has already been loaded
            if (currentTemplate.length) {
                if (currentTemplate.html().length) {
                    var changeTemplate = false;

                    if (templateChanged) {
                        // If a different template was selected we want to warn the user
                        changeTemplate = confirm(this.config.overwriteTemplateConfirm);
                    }
                    else {
                        // Template wasn't changed, so a new recipient was entered
                        changeTemplate = true;
                    }

                    if (changeTemplate) {
                        // Change the html of the existing email template
                        currentTemplate.html(htmlPart);
                        // Since editorValue is actually an array of elements we can't easily convert it back to text
                        var container = $('<div>');
                        // Add the (edited) html to the newly created container
                        container.append(editorValue);
                        // Get the text version of the new html
                        newEditorValue = container[0].innerHTML;
                    }
                }
            }
            else {
                // No email template loaded so create our email template container
                var emailTemplate = '<div id="compose-email-template">' + htmlPart + '</div>';
                // Append the existing text
                newEditorValue = emailTemplate + '<br>' + editor.getValue();
            }

            if (newEditorValue.length) {
                editor.setValue(newEditorValue + '<br>');
                this.resizeEditor();
            }
        }
    }
})(jQuery, window, document);
