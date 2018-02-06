(function($, window, document) {
    var editor;

    window.HLInbox = {
        config: {
            accountDeactivatedMessage: 'Your account doesn\'t seem to be active. Please activate your account to view your email.',
            inboxCcInput: '.inbox-compose .mail-to .inbox-cc',
            inboxBccInput: '.inbox-compose .mail-to .inbox-bcc',
            singleMessageSelector: '.inbox-content .view-message',
            templateField: '#id_template',
            inboxComposeSubmit: '.inbox-compose [type="submit"]',
            wysiHtmlToolbar: '#wysihtml5-toolbar',
            textEditorId: 'id_body_html',
            replyButton: '.reply-btn',
            tagsAjaxSelector: '.tags-ajax',
            emailAccountInput: '#id_send_from',
            sendToNormalField: '#id_send_to_normal',
            emptyTemplateAttachmentRow: '#empty-template-attachment-row',
            templateAttachmentDeleteButton: '#template-attachments [data-formset-delete-button]',
            templateAttachmentsDiv: '#template-attachments',
            templateAttachmentName: '.template-attachment-name',
            templateAttachmentIds: '#template-attachment-ids',
            templateAttachmentId: '.template-attachment-id',
            templateAttachmentRow: '.template-attachment-row',
            templateAttachmentUpload: '#fileupload',
            currentTemplate: null,
            previousSendToNormalLength: 0,
            firstLoad: true,
            mailAttachmentsOffset: 0,
        },

        init: function(config) {
            var self = this;

            // Setup config
            if (typeof config === 'object') {
                $.extend(this.config, config);
            }

            if (self.config.firstLoad) {
                self.config.firstLoad = false;
                self.initListeners();
                Metronic.initUniform();
            }
        },

        initListeners: function() {
            var self = this;
            var cf = self.config;
            var parts = [];
            var recipients = [];
            var element;

            $('body')
                .on('click', cf.inboxCcInput, function() {
                    // Handle compose/reply cc input toggle.
                    self.handleAdditionalRecipientsInput('cc');
                })
                .on('click', cf.inboxBccInput, function() {
                    // Handle compose/reply bcc input toggle.
                    self.handleAdditionalRecipientsInput('bcc');
                })
                .on('change', cf.emailAccountInput, function() {
                    self.changeTemplateField.call(self, cf.templateField, false);
                })
                .on('change', cf.templateField, function() {
                    self.changeTemplateField.call(self, this, true);
                })
                .on('change', cf.sendToNormalField, function() {
                    var previousSendToNormalLength = self.config.previousSendToNormalLength;
                    var inputLength = $(this).select2('data').length;

                    self.config.previousSendToNormalLength = inputLength;

                    // Don't do anything if we have more than two recipients
                    // or if we're just removing recipients.
                    if (!(inputLength === 1 && !previousSendToNormalLength)) {
                        return;
                    }

                    self.changeTemplateField.call(self, cf.templateField, false);
                })
                .on('click', cf.replyButton, function() {
                    // Open links when clicking the reply button.
                    $('.inbox-view').hide();
                    $('.inbox-loading').show();
                })
                .on('click', cf.inboxComposeSubmit, function(event) {
                    self.handleInboxComposeSubmit(this, event);
                })
                .on('change', cf.tags, function() {
                    self.handleTagsAjaxChange(this);
                })
                .on('click', cf.templateAttachmentDeleteButton, function() {
                    var attachmentRow = $(this).closest('.form-group');
                    self.handleTemplateAttachmentsChange(attachmentRow);
                })
                .on('formDeleted', cf.templateAttachmentUpload, function() {
                    // Hide instead of remove upload form element,
                    // removing breaks with attachment id's when forwarding email with attachements.
                    $('[data-formset-form-deleted]').hide();
                });

            $('.inbox-compose input').on('keydown keyup keypress', function(event) {
                // Make sure pressing enter doesn't do anything (except selecting something in a dropdown)
                if (event.which === 13) {
                    event.preventDefault();
                }
            });

            $('.inbox-compose input').on('paste', function(event) {
                element = $(this).closest('.select2-container');

                // Delegate to next cycle.
                setTimeout(function() {
                    parts = event.target.value.trim().split(' ');
                    recipients = element.select2('data');

                    parts.map(email => {
                        recipients.push({
                            id: email,
                            text: email,
                            object_id: null,
                        });
                    });

                    element.select2('data', recipients);
                }, 0);
            });
        },

        customParser: function() {
            function parse(elementOrHtml, rules, context, cleanUp) {
                return elementOrHtml;
            }

            return parse;
        },

        initEmailCompose: function(emailComposeConfig) {
            var self = this;
            var decodedEditorValue;
            var $composeEmailTemplate;

            if (typeof emailComposeConfig === 'object') {
                $.extend(self.config, emailComposeConfig);
            }

            self.initWysihtml5();

            // If loadDefaultTemplate isn't set there was an error, so don't do any template loading
            if (self.config.loadDefaultTemplate !== null) {
                if (self.config.loadDefaultTemplate) {
                    // If no template was given in the url, load the default template
                    self.loadDefaultEmailTemplate();
                } else {
                    // Otherwise trigger change event so the given template gets loaded
                    $(self.config.templateField).val(self.config.template).change();
                }
            }

            if (self.config.recipient) {
                $(self.config.sendToNormalField).select2('data', self.config.recipient);
            }

            // Decode special chars
            decodedEditorValue = self.decodeEntities(editor.getValue());
            $composeEmailTemplate = $(decodedEditorValue).closest('#compose-email-template');

            // If there's a template, we're dealing with a draft, so set currentTemplate
            if ($composeEmailTemplate.length) {
                self.config.currentTemplate = $composeEmailTemplate[0].innerHTML;
            }
        },

        // Courtesy of Robert K/Ian Clark @ http://stackoverflow.com/questions/5796718/html-entity-decode/9609450#9609450
        decodeEntities: function(str) {
            var decodedString = str;

            // This prevents any overhead from creating the object each time
            var element = document.createElement('div');

            if (str && typeof str === 'string') {
                // Strip script/html tags
                decodedString = decodedString.replace(/<script[^>]*>([\S\s]*?)<\/script>/gmi, '');
                decodedString = decodedString.replace(/<\/?\w(?:[^"'>]|"[^"]*"|'[^']*')*>/gmi, '');
                element.innerHTML = decodedString;
                decodedString = element.textContent;
                element.textContent = '';
            }

            return decodedString;
        },

        initWysihtml5: function() {
            var self = this;
            var toolbarOffset;
            var toolbar;
            var scrollHeight;
            var mailAttachmentsHeight;
            // Only set the navBarHeight if we're dealing with a 'big' screen.
            var navBarHeight = $(window).width() > 992 ? $('.page-header').height() : 0;

            editor = new wysihtml5.Editor(self.config.textEditorId, {
                toolbar: 'wysihtml5-toolbar',
                parser: self.customParser(),
                handleTables: false,
                doubleLineBreakEscapesBlock: false,
            });

            toolbar = $(self.config.wysiHtmlToolbar);

            editor.observe('load', function() {
                // Initial value is most likely reply/forward text, so store it for later usage
                self.config.initialEditorValue = editor.getValue();
                // Extra div is needed so the editor auto resizes
                editor.setValue(self.config.initialEditorValue + '<div id="resize-div"></div>');

                $(this.composer.element).on('keydown paste change focus blur', function() {
                    self.resizeEditor();
                });

                // Make the editor the correct height on load
                self.resizeEditor();

                // Check the initial position of the toolbar.
                toolbarOffset = toolbar.offset().top;

                mailAttachmentsHeight = $('.attachments_formset_wrapper').height();

                $(window).scroll(function() {
                    scrollHeight = $(window).scrollTop() + navBarHeight;

                    // Check the position of our scroll.
                    // Check if the (fixed) toolbar has reached the location of the attachments.
                    if (scrollHeight > toolbarOffset && scrollHeight <= self.config.mailAttachmentsOffset - mailAttachmentsHeight * 2) {
                        // Stick the toolbar in a fixed positon once the window's
                        // scroll passes the toolbar.
                        toolbar.css({position: 'fixed', top: navBarHeight + 'px'});
                    } else {
                        // Otherwise it should just be in normal position.
                        toolbar.css({position: 'static'});
                    }
                });
            });

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

        resizeEditor: function() {
            $('.wysihtml5-sandbox')[0].style.height = editor.composer.element.scrollHeight + 'px';

            // We want to move the toolbar back once it reaches the attachments location.
            this.config.mailAttachmentsOffset = $('.attachments_formset_wrapper').offset().top;
        },

        handleAdditionalRecipientsInput: function(inputType) {
            var $ccLink = $('.inbox-compose .mail-to .inbox-' + inputType);
            var $inputField = $('.inbox-compose .input-' + inputType);

            $ccLink.hide();
            $inputField.show();
            $('.close', $inputField).click(function() {
                $inputField.hide();
                $ccLink.show();
                $inputField.find('.tags').select2('val', '');
            });
        },

        changeTemplateField: function(templateField, templateChanged) {
            var self = this;
            var selectedTemplate;
            var recipientId = null;
            var emailAccountId;
            var url;
            var recipient;

            if (self.config.templateList) {
                selectedTemplate = parseInt($(templateField).val());
                emailAccountId = $(self.config.emailAccountInput).val();

                if (emailAccountId) {
                    if (selectedTemplate && templateChanged) {
                        recipient = $('#id_send_to_normal').select2('data')[0];

                        if (typeof recipient !== 'undefined' && typeof recipient.object_id !== 'undefined') {
                            // Check if a contact has been entered.
                            recipientId = recipient.object_id;
                        } else if (self.config.sender !== '' && self.config.sender !== null) {
                            // If it's a reply there might be contact set.
                            recipientId = self.config.sender;
                            self.config.sender = null;
                        }

                        // Always get a template.
                        url = self.config.getTemplateUrl + selectedTemplate + '/';

                        url += '?emailaccount_id=' + emailAccountId;

                        if (recipient && recipient.account) {
                            url += `&account_id=${recipient.account.id}`;
                        }

                        if (recipientId) {
                            url += '&contact_id=' + recipientId;
                        }

                        if (self.config.documentId) {
                            url += '&document_id=' + self.config.documentId + '&recipient_email=' + self.config.recipientEmail;
                        }

                        $.getJSON(url, function(data) {
                            self.setNewEditorValue(data, templateChanged);
                        });
                    } else {
                        self.loadDefaultEmailTemplate();
                    }
                } else {
                    toastr.error('I couldn\'t load the template because your email account doesn\'t seem to be set. Please check your email account and try again');
                }
            }
        },

        submitForm: function(buttonName, $form) {
            var self = this;
            var templateContent = '';

            // Remove unnecessary html.
            var $containerDiv = $('<div id="email-container-div">');
            $containerDiv[0].innerHTML = HLInbox.getEditor().getValue();

            // Get template content if we're not dealing with the creation of a draft and there is a template set.
            if (buttonName !== 'submit-save' && $containerDiv.find('#compose-email-template').length) {
                templateContent = $containerDiv.find('#compose-email-template')[0].innerHTML;

                // Remove email template div and resize div and only keep user typed text.
                $containerDiv.find('#compose-email-template').remove();
            }

            $containerDiv.find('#resize-div').remove();

            /**
             * You'd expect HLInbox.getEditor().setValue or $('#id_body_html').html
             * would work to set the value of the textarea.
             * Sadly they don't, which is why .val is used.
             */
            $('#' + self.config.textEditorId).val(templateContent + '<br>' + $containerDiv[0].innerHTML);

            // Make sure both buttons of the same name are set to the loading state.
            $('button[name="' + buttonName + '"]').button('loading');

            // No validation needed, remove attachments to prevent unneeded uploading.
            $('[id|=id_attachments]:file').filter(function() {
                return $(this).data('formset-disabled') === true;
            }).remove();

            Metronic.blockUI($('.inbox-content'), false, '');

            $form.submit();
        },

        handleInboxComposeSubmit: function(inboxCompose, event) {
            var draftPk;
            var buttonName = $(inboxCompose).attr('name');
            var $form = $($(inboxCompose).closest('form'));

            event.preventDefault();

            if (buttonName === 'submit-save') {
                draftPk = $('#id_draft_pk').val();
                // If we are saving a (existing) draft, change url
                if (draftPk) {
                    $form.attr('action', '/messaging/email/draft/' + draftPk + '/');
                } else {
                    $form.attr('action', '/messaging/email/draft/');
                }
            }

            HLInbox.submitForm(buttonName, $form);
        },

        handleTagsAjaxChange: function(tagsAjax) {
            // Select2 doesn't remove certain values (values with quotes), so make sure that the value of the field is correct
            var values = [];
            var data = $(tagsAjax).select2('data');
            var recipientData;
            var i;

            for (i = 0; i < data.length; i++) {
                recipientData = data[i];
                values.push(recipientData.id);
            }

            $(tagsAjax).val(values.join());
        },

        getEditor: function() {
            return editor;
        },

        destroyEditor: function() {
            if (editor && editor !== null) {
                editor.destroy();
                editor = null;
            }
        },

        loadDefaultEmailTemplate: function() {
            var self = this;
            var emailAccountId = $(self.config.emailAccountInput).val();
            var url;

            if (emailAccountId) {
                url = self.config.defaultEmailTemplateUrl + emailAccountId + '/';

                $.getJSON(url, function(data) {
                    if (data.template_id) {
                        $(self.config.templateField).select2('val', data.template_id).change();
                    }
                });
            } else {
                toastr.error('Sorry, I couldn\'t load your default email template. You could try reloading the page');
            }
        },

        setNewEditorValue: function(data, templateChanged) {
            var self = this;
            var htmlPart = data.template;
            // getValue returns a string, so convert to elements.
            var editorValue = $(editor.getValue());
            var currentTemplate = editorValue.closest('#compose-email-template');
            var newEditorValue = '';
            var addedTemplateText = '';
            var diff = {};
            var container;
            var emailTemplate;
            var message;

            if (data.errors.document) {
                toastr.error(data.errors.document, 'Oops');
            }

            // Check if an email template has already been loaded.
            if (currentTemplate.length) {
                if (currentTemplate.html().length) {
                    if (templateChanged) {
                        // If a different template was selected we want to warn the user.
                        message = messages.alerts.email.overwriteTemplateConfirm;
                    } else {
                        // Template wasn't changed, so a new recipient was entered.
                        // Check if the user wants to reload the template.
                        message = messages.alerts.email.reloadTemplateConfirm;
                    }

                    swal({
                        title: 'Reload template',
                        html: message,
                        type: 'info',
                        showCancelButton: true,
                        confirmButtonText: 'Yes',
                        cancelButtonText: 'No',
                    }).then(function(isConfirm) {
                        if (isConfirm) {
                            if (self.config.currentTemplate) {
                                // First time changing a draft needs a different operation.
                                // We want to check if the draft template differs from the default.
                                if (self.config.messageType === 'draft' && htmlPart === self.config.currentTemplate) {
                                    diff = JsDiff.diffChars(currentTemplate.html(), htmlPart);
                                } else {
                                    // Otherwise compare the current editor value with the current template.
                                    diff = JsDiff.diffChars(currentTemplate.html(), self.config.currentTemplate);
                                }

                                diff.forEach(function(part) {
                                    // Get all text that was changed/added.
                                    if (part.added || part.removed) {
                                        addedTemplateText += part.value;
                                    }
                                });
                            }

                            self.config.currentTemplate = htmlPart;

                            // Change the html of the existing email template and add text that was added to the template.
                            currentTemplate.html(htmlPart + addedTemplateText);
                            // Since editorValue is actually an array of elements we can't easily convert it back to text.
                            container = $('<div>');
                            // Add the (edited) html to the newly created container.
                            container.append(editorValue);
                            // Get the text version of the new html.
                            newEditorValue = container[0].innerHTML;

                            self.processNewEditorValue(newEditorValue, data);
                        }
                    }).done();
                }
            } else {
                // No email template loaded so create our email template container.
                emailTemplate = '<div id="compose-email-template">' + htmlPart + '</div>';
                // Append the existing text
                newEditorValue = emailTemplate + '<br>' + editor.getValue();

                self.config.currentTemplate = htmlPart;

                self.processNewEditorValue(newEditorValue, data);
            }

            // Only overwrite the subject if a new email is being created.
            if (this.config.messageType === 'new' && data.template_subject !== '') {
                $('#id_subject').val(data.template_subject);
            }
        },

        processNewEditorValue: function(newEditorValue, data) {
            if (newEditorValue.length) {
                editor.setValue(newEditorValue);
                this.resizeEditor();
                this.processAttachments(data.attachments);
            }
        },

        processAttachments: function(attachments) {
            var cf = this.config;
            var i;
            var attachment;
            var attachmentIds = [];
            var attachmentRow;

            // Clear any existing template attachments.
            $(cf.templateAttachmentsDiv).empty();

            for (i = 0; i < attachments.length; i++) {
                attachment = attachments[i];
                attachmentIds.push(attachment.id);

                attachmentRow = $(cf.emptyTemplateAttachmentRow).clone();
                attachmentRow.find(cf.templateAttachmentName).html(attachment.name);
                attachmentRow.find(cf.templateAttachmentId).val(attachment.id);
                attachmentRow.removeAttr('id');
                attachmentRow.removeClass('hidden');

                $(cf.templateAttachmentsDiv).append(attachmentRow);
            }

            $(cf.templateAttachmentIds).val(attachmentIds);
        },

        handleTemplateAttachmentsChange: function(attachmentRow) {
            var self = this;
            var cf = self.config;
            var newAttachmentIds = [];
            var attachments = $(cf.templateAttachmentRow);
            var rowAttachmentName = attachmentRow.find(cf.templateAttachmentName);
            var attachmentId;

            if (rowAttachmentName.hasClass('mark-deleted')) {
                rowAttachmentName.removeClass('mark-deleted');
            } else {
                rowAttachmentName.addClass('mark-deleted');
            }

            attachmentRow.find('[data-formset-delete-button]').toggleClass('hidden');
            attachmentRow.find('[data-formset-undo-delete]').toggleClass('hidden');

            attachments.each(function() {
                if (!$(this).find(cf.templateAttachmentName).hasClass('mark-deleted')) {
                    attachmentId = $(this).find(cf.templateAttachmentId).val();
                    if (attachmentId !== '') {
                        // Make sure the value of the empty attachment row doesn't get added.
                        newAttachmentIds.push(attachmentId);
                    }
                }
            });

            $(cf.templateAttachmentIds).val(newAttachmentIds);
        },

        setSuccesURL: function(previousState) {
            if (previousState !== null) {
                $("input[name='success_url']").val(previousState);
            }
        },

        setCurrentInbox: function(currentInbox) {
            if (currentInbox !== null) {
                $("input[name='current_inbox']").val(currentInbox);
            }
        },
    };
})(jQuery, window, document);
