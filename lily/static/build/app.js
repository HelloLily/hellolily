(function(angular){
'use strict';
(function(angular){
'use strict';
/**
 * app.accounts manages all routes, controllers eg.
 * that relate to Account.
 */
angular.module('app.accounts', [
    'ngCookies',
    'ui.bootstrap',
    'ui.slimscroll',
    'app.accounts.services',
    'app.cases.services',
    'app.contacts.services',
    'app.email.services',
    'app.notes'
]);

})(angular);
(function(angular){
'use strict';
angular.module('app.cases', [
    // Angular dependencies
    'ngCookies',

    // 3rd party
    'ui.bootstrap',

    // Lily dependencies
    'app.accounts.services',
    'app.cases.services',
    'app.email.services',
    'app.contacts.services',
    'app.notes'
]);

})(angular);
(function(angular){
'use strict';
angular.module('app.contacts', [
    // Angular dependencies
    'ngCookies',

    // 3rd party
    'ui.bootstrap',

    // Lily dependencies
    'app.accounts.services',
    'app.cases.services',
    'app.contacts.services',
    'app.notes',
    'app.email.services'
]);

})(angular);
(function(angular){
'use strict';
angular.module('app.dashboard', [
    'app.dashboard.directives',
    'app.users.services',
    'chart.js',
    'ui.slimscroll'
]);

})(angular);
(function(angular){
'use strict';
angular.module('app.deals', [
    // Angular dependencies
    'ngCookies',

    // 3rd party
    'ui.bootstrap',
    'ui.select',

    // Lily dependencies
    'app.deals.services'
]);

})(angular);
(function(angular){
'use strict';
angular.module('app.email', [
    // 3rd party
    'ui.bootstrap',
    'ui.router',

    // Lily dependencies
    'app.email.services',
    'app.email.directives',
    'app.services'
]);

})(angular);
(function(angular){
'use strict';
angular.module('app.preferences', [
    'ui.bootstrap',
    'ui.slimscroll',
    'app.email.services',
    'app.services',
    'app.users.services',
    'app.users.filters'
]);

})(angular);
(function(angular){
'use strict';
angular.module('app.utils', [
    'ngAnimate'
]);

})(angular);
(function(angular){
'use strict';
angular.module('app.accounts.directives', []);

})(angular);
(function(angular){
'use strict';
angular.module('app.accounts.services', ['ngResource']);

})(angular);
(function(angular){
'use strict';
angular.module('app.base', [
    'ui.bootstrap'
]);

})(angular);
(function(angular){
'use strict';
/**
 * app.directives is a container for all global lily related Angular directives
 */
angular.module('app.directives', []);

})(angular);
(function(angular){
'use strict';
angular.module('app.filters', []);

})(angular);
(function(angular){
'use strict';
angular.module('app.services', []);

})(angular);
(function(angular){
'use strict';
angular.module('app.cases.directives', []);

})(angular);
(function(angular){
'use strict';
angular.module('app.cases.services', ['ngResource']);

})(angular);
(function(angular){
'use strict';
angular.module('app.contacts.directives', []);

})(angular);
(function(angular){
'use strict';
angular.module('app.contacts.services', ['ngResource']);

})(angular);
(function(angular){
'use strict';
angular.module('app.dashboard.directives', []);

})(angular);
(function(angular){
'use strict';
angular.module('app.deals.directives', []);

})(angular);
(function(angular){
'use strict';
angular.module('app.deals.services', []);

})(angular);
(function(angular){
'use strict';
angular.module('app.email.directives', []);

})(angular);
(function(angular){
'use strict';
angular.module('app.email.services', ['ngResource']);

})(angular);
(function(angular){
'use strict';
angular.module('app.notes', ['ngResource']);

})(angular);
(function(angular){
'use strict';
angular.module('app.users.filters', []);

})(angular);
(function(angular){
'use strict';
angular.module('app.users.services', ['ngResource']);

})(angular);
(function(angular){
'use strict';
angular.module('app.utils.directives', []);

})(angular);
(function(angular){
'use strict';
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

ga('create', 'UA-60721851-1', 'auto');

})(angular);
(function(angular){
'use strict';
/**
 * App Module is the entry point for Lily related Angular code
 */
angular.module('app', [
    'ui.router',
    'ui.bootstrap',
    'ngAnimate',
    'ngResource',
    'ngSanitize',
    'ncy-angular-breadcrumb',

    // Controllers
    'app.accounts',
    'app.base',
    'app.cases',
    'app.contacts',
    'app.dashboard',
    'app.deals',
    'app.email',
    'app.preferences',
    'app.templates',
    'app.utils',

    // Directives
    'app.directives',
    'app.accounts.directives',
    'app.cases.directives',
    'app.contacts.directives',
    'app.deals.directives',
    'app.utils.directives',

    // Google Analytics
    'angulartics',
    'angulartics.google.analytics',

    // Services
    'app.services',

    // Filters
    'app.filters'
]);

/* Setup global settings */
angular.module('app').factory('settings', settings);

settings.$inject = ['$rootScope'];
function settings ($rootScope) {
    // supported languages
    var settings = {
        layout: {
            pageSidebarClosed: false // sidebar state
        }
    };

    $rootScope.settings = settings;

    return settings;
}

angular.module('app').config(appConfig);

appConfig.$inject = [
    '$animateProvider',
    '$breadcrumbProvider',
    '$controllerProvider',
    '$httpProvider',
    '$resourceProvider',
    '$urlRouterProvider'
];
function appConfig ($animateProvider, $breadcrumbProvider, $controllerProvider, $httpProvider, $resourceProvider, $urlRouterProvider){
    // Don't strip trailing slashes from calculated URLs, because django needs them
    $breadcrumbProvider.setOptions({
        templateUrl: 'base/breadcrumbs.html',
        includeAbstract: true
    });
    $controllerProvider.allowGlobals();
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    $resourceProvider.defaults.stripTrailingSlashes = false;
    $urlRouterProvider.otherwise('/');
    // prevent ng-animation on fa-spinner
    $animateProvider.classNameFilter(/^((?!(fa-spin)).)*$/);
}

/* Init global settings and run the app */
angular.module('app').run(runApp);

runApp.$inject = ['$rootScope', '$state', 'settings'];
function runApp ($rootScope, $state, settings) {
    $rootScope.$state = $state; // state to be accessed from view
    $rootScope.currentUser = currentUser;
    $rootScope.settings = settings;
}


})(angular);
(function(angular){
'use strict';
$('body').on('blur', 'input[name^="phone"]', function() {
    // Format telephone number
    var $phoneNumberInput = $(this);
    var phone = $phoneNumberInput.val();
    if (phone.match(/[a-z]|[A-Z]/)) {
        // if letters are found, skip formatting: it may not be a phone field after all
        return false;
    }

    // Match on mobile phone nrs e.g. +316 or 06, so we can automatically set the type to mobile.
    if (phone.match(/^\+316|^06/)) {
        var typeId = $phoneNumberInput.attr('id').replace('raw_input', 'type');
        $('#' + typeId).select2('val', 'mobile');
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
        phone = '+31' + phone;
    }

    if (phone.startsWith('+310')) {
        phone = '+31' + phone.substring(4);
    }
    $phoneNumberInput.val(phone);
});

$('body').on('change', 'select[id*="is_primary"]', function(e) {
    if($(e.currentTarget).val() == 'True'){
        $('select[id*="is_primary"]').each(function(i){
            if($(this).is('select') && $(this).val() == 'True'){
                $(this).val('False');
            }
        });
        $(e.currentTarget).val('True');
        HLSelect2.init();
    }
});

function addBusinessDays(date, businessDays) {
    var weeks = Math.floor(businessDays/5);
    var days = businessDays % 5;
    var day = date.getDay();
    if (day === 6 && days > -1) {
       if (days === 0) {days-=2; day+=2;}
       days++; dy -= 6;}
    if (day === 0 && days < 1) {
       if (days === 0) {days+=2; day-=2;}
       days--; day += 6;}
    if (day + days > 5) days += 2;
    if (day + days < 1) days -= 2;
    date.setDate(date.getDate() + weeks * 7 + days);
    return date;
}

})(angular);
(function(angular){
'use strict';
(function($, window, document, undefined) {
    var currentStatus;

    window.HLCases = {
        config: {
            caseUpdateUrl: '/cases/update/status/',
            caseUpdateAssignedToUrl: '/cases/update/assigned_to/',
            caseId: null,
            statusSpan: '#status',
            statusDiv: '#case-status',
            parcelProviderSelect: '#id_parcel_provider',
            parcelIdentifierInput: '#id_parcel_identifier',
            assignedToField: '#id_assigned_to',
            assignToMeButton: '.assign-me-btn',
            currentAssignedTo: null
        },

        init: function(config) {
            // Setup config
            var self = this;
            if ($.isPlainObject(config)) {
                $.extend(self.config, config);
            }
            self.initListeners();
            self.setCurrentStatus();
        },

        initListeners: function() {
            var self = this,
                cf = self.config;

            $(cf.statusDiv).on('click', function(event) {
               self.changeStatus.call(self, event);
            });

            $(cf.parcelProviderSelect).on('change', function() {
               self.changedParcelProviderSelect.call(self, this);
            });

            $(cf.assignToMeButton).on('click', function() {
                self.changeAssignedTo.call(self, this);
            });
        },

        setCurrentStatus: function() {
            currentStatus = $('input[name=radio]:checked', this.config.statusDiv).closest('label').attr('for');
        },

        changeStatus: function(event) {
            var self = this,
                cf = self.config;
            var radio_element = $('#' + $(event.target).closest('label').attr('for'));
            if(radio_element.attr('id') != currentStatus) {
                var $radio_element = $(radio_element);
                if (cf.caseId != null) {
                    $.ajax({
                        url: cf.caseUpdateUrl + cf.caseId + '/',
                        type: 'POST',
                        data: {
                            status: $radio_element.val()
                        },
                        beforeSend: HLApp.addCSRFHeader,
                        dataType: 'json'
                    }).done(function (data) {
                        currentStatus = $radio_element.attr('id');
                        $(cf.statusSpan).text(data.status);
                        // loads notifications if any
                        load_notifications();
                    }).fail(function () {
                        // reset selected status
                        $(radio_element).attr('checked', false).closest('label').removeClass('active');
                        $('#' + currentStatus).attr('checked', true).closest('label').addClass('active');
                        // loads notifications if any
                        load_notifications();
                    });
                }
            }
        },

        changedParcelProviderSelect: function(select) {
            // Remove identifier if the provider is removed
            var $select = $(select);
            if (!$select.val()) {
                $(this.config.parcelIdentifierInput).val('');
            }
        },

        changeAssignedTo: function () {
            var self = this,
                cf = self.config;

            var assignee = null;

            if (cf.currentAssignedTo != currentUser.id) {
                assignee = currentUser.id;
            }

            if (cf.caseId != null) {
                $.ajax({
                    url: cf.caseUpdateAssignedToUrl + cf.caseId + '/',
                    type: 'POST',
                    data: {
                        assignee: assignee
                    },
                    beforeSend: HLApp.addCSRFHeader,
                    dataType: 'json'
                }).done(function (data) {
                    var assignee = data.assignee;

                    // TODO: This will be made prettier once we Angularify the detail page(s)
                    if (assignee) {
                        $('.summary-data.assigned-to').html(data.assignee.name);
                        $('.assign-me-btn').html('Unassign');
                        cf.currentAssignedTo = data.assignee.id;
                    }
                    else {
                        $('.summary-data.assigned-to').html('Unassigned');
                        $('.assign-me-btn').html('Assign to me');
                        cf.currentAssignedTo = null;
                    }
                }).always(function () {
                    // loads notifications if any
                    load_notifications();
                });
            }
        },

        addAssignToMeButton: function() {
            var self = this;
            var assignToMeButton = $('<button class="btn btn-link assign-me-btn">Assign to me</button>');

            $(self.config.assignedToField).after(assignToMeButton);

            assignToMeButton.click(function (event) {
                event.preventDefault();
                $(self.config.assignedToField).val(currentUser.id).change();
            });
        }
    }
})(jQuery, window, document);

})(angular);
(function(angular){
'use strict';
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

            // TODO: LILY-953: Change this to API endpoint
            var parameterChoices = {
                "Contact": {
                    "contact.full_name": "Full name",
                    "contact.work_phone": "Work phone",
                    "contact.last_name": "Last name",
                    "contact.twitter": "Twitter",
                    "contact.mobile_phone": "Mobile phone",
                    "contact.first_name": "First name",
                    "contact.linkedin": "Linkedin",
                    "contact.preposition": "Preposition",
                    "contact.primary_email": "Primary email",
                    "contact.account_city": "Account city"
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

            var $containerDiv = $('<div>');
            $containerDiv[0].innerHTML = HLInbox.getEditor().getValue();
            // Remove resize div
            $containerDiv.find('#resize-div').remove();

            /**
             * You'd expect HLInbox.getEditor().setValue or $('#id_body_html').html
             * would work to set the value of the textarea.
             * Sadly they don't, which is why .val is used
             */
            $('#id_body_html').val($containerDiv[0].innerHTML);

            var $form = $($(submitButton).closest('form'));

            Metronic.blockUI($('.inbox-content'), false, '');

            $form.submit();
        }
    }
})(jQuery, window, document);


})(angular);
(function(angular){
'use strict';
(function ($, window, document, undefined) {
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
            replyButton: '.reply-btn',
            tagsAjaxSelector: '.tags-ajax',
            emailAccountInput: '#id_send_from',
            sendToNormalField: '#id_send_to_normal',
            overwriteTemplateConfirm: 'Selecting a different template will overwrite the text you\'ve typed. Do you want to load the template anyway?',
            emptyTemplateAttachmentRow: '#empty-template-attachment-row',
            templateAttachmentDeleteButton: '#template-attachments [data-formset-delete-button]',
            templateAttachmentUndoDeleteButton: '#template-attachments [data-formset-undo-delete]',
            templateAttachmentsDiv: '#template-attachments',
            templateAttachmentName: '.template-attachment-name',
            templateAttachmentIds: '#template-attachment-ids',
            templateAttachmentId: '.template-attachment-id',
            templateAttachmentRow: '.template-attachment-row',
            currentTemplate: null,
            previousSendToNormalLength: 0
        },

        init: function (config) {
            var self = this;

            // Setup config
            if (typeof (config === 'object')) {
                $.extend(this.config, config);
            }

            self.initListeners();
            Metronic.initUniform();
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
                .on('change', cf.emailAccountInput, function () {
                    self.changeTemplateField.call(self, cf.templateField, false);
                })
                .on('change', cf.templateField, function () {
                    self.changeTemplateField.call(self, this, true);
                })
                .on('change', cf.sendToNormalField, function () {
                    var previousSendToNormalLength = self.config.previousSendToNormalLength;

                    var inputLength = $(this).select2('data').length;
                    self.config.previousSendToNormalLength = inputLength;

                    // Don't do anything if it's just an extra recipient being added/removed
                    // or the last recipient is removed
                    if (inputLength > 1 || inputLength < previousSendToNormalLength) {
                        return false;
                    }

                    self.changeTemplateField.call(self, cf.templateField, false);
                })
                .on('click', cf.replyButton, function () {
                    // Open links when clicking the reply button
                    $('.inbox-view').hide();
                    $('.inbox-loading').show();
                })
                .on('click', cf.inboxComposeSubmit, function (event) {
                    self.handleInboxComposeSubmit(this, event);
                })
                .on('change', cf.tags, function () {
                    self.handleTagsAjaxChange(this);
                })
                .on('click', cf.templateAttachmentDeleteButton, function () {
                    var attachmentRow = $(this).closest('.form-group');
                    self.handleTemplateAttachmentsChange(attachmentRow);
                })
                .on('click', cf.templateAttachmentUndoDeleteButton, function () {
                    var attachmentRow = $(this).closest('.form-group');
                    self.handleTemplateAttachmentsChange(attachmentRow);
                });

            $('.inbox-compose input').on('keydown keyup keypress', function(event) {
                // Make sure pressing enter doesn't do anything (except selecting something in a dropdown)
                if (event.which == 13) {
                    event.preventDefault();
                }
            });
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
                $.extend(self.config, emailComposeConfig);
            }

            self.initWysihtml5();

            // If loadDefaultTemplate isn't set there was an error, so don't do any template loading
            if (self.config.loadDefaultTemplate !== null) {
                if (self.config.loadDefaultTemplate) {
                    // If no template was given in the url, load the default template
                    self.loadDefaultEmailTemplate();
                }
                else {
                    // Otherwise trigger change event so the given template gets loaded
                    $(self.config.templateField).val(self.config.template).change();
                }
            }

            if (self.config.recipient) {
                $(self.config.sendToNormalField).select2('data', self.config.recipient);
            }

            // Decode special chars
            var decodedEditorValue = self.decodeEntities(editor.getValue());
            var $composeEmailTemplate = $(decodedEditorValue).closest('#compose-email-template');

            // If there's a template, we're dealing with a draft, so set currentTemplate
            if ($composeEmailTemplate.length) {
                self.config.currentTemplate = $composeEmailTemplate[0].innerHTML;
            }
        },

        // Courtesy of Robert K/Ian Clark @ http://stackoverflow.com/questions/5796718/html-entity-decode/9609450#9609450
        decodeEntities: function (str) {
            // This prevents any overhead from creating the object each time
            var element = document.createElement('div');

            if (str && typeof str === 'string') {
                // Strip script/html tags
                str = str.replace(/<script[^>]*>([\S\s]*?)<\/script>/gmi, '');
                str = str.replace(/<\/?\w(?:[^"'>]|"[^"]*"|'[^']*')*>/gmi, '');
                element.innerHTML = str;
                str = element.textContent;
                element.textContent = '';
            }

            return str;
        },

        initWysihtml5: function () {
            var self = this;

            editor = new wysihtml5.Editor('id_body_html', {
                toolbar: 'wysihtml5-toolbar',
                parser: self.customParser(),
                handleTables: false
            });

            editor.observe('load', function () {
                // Initial value is most likely reply/forward text, so store it for later usage
                self.config.initialEditorValue = editor.getValue();
                // Extra div is needed so the editor auto resizes
                editor.setValue(self.config.initialEditorValue + '<div id="resize-div"></div>');

                $(this.composer.element).on('keydown paste change focus blur', function () {
                    self.resizeEditor();
                });

                // Make the editor the correct height on load
                self.resizeEditor();
            });

            // Set heading properly after change
            var toolbar = $(self.config.wysiHtmlToolbar);
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
            if (self.config.templateList) {
                var selectedTemplate = parseInt($(templateField).val());
                var recipientId = null;
                var emailAccountId = $(self.config.emailAccountInput).val();

                if (emailAccountId) {
                    if (selectedTemplate) {
                        var recipient = $('#id_send_to_normal').select2('data')[0];

                        if (typeof recipient !== 'undefined' && typeof recipient.object_id !== 'undefined') {
                            // Check if a contact has been entered
                            recipientId = recipient.object_id;
                        }
                        else if (self.config.sender !== '' && self.config.sender != null) {
                            // If it's a reply there might be contact set
                            recipientId = self.config.sender;
                            self.config.sender = null;
                        }

                        // Always get a template
                        var url = self.config.getTemplateUrl + selectedTemplate + '/';

                        if (recipientId != null) {
                            // If a recipient has been set we can set extra url parameters
                            url += '?contact_id=' + recipientId + '&emailaccount_id=' + emailAccountId;
                        }
                        else {
                            url += '?emailaccount_id=' + emailAccountId;
                        }

                        $.getJSON(url, function (data) {
                            self.setNewEditorValue(data, templateChanged);
                        });
                    }
                }
                else {
                    toastr.error('I couldn\'t load the template because your email account doesn\'t seem to be set. Please check your email account and try again');
                }
            }
        },

        submitForm: function(buttonName, $form) {
            var self = this;
            // Remove unnecessary html
            var $containerDiv = $('<div id="email-container-div">');
            $containerDiv[0].innerHTML = HLInbox.getEditor().getValue();

            var templateContent = '';
            // Get template content if we're not dealing with the creation of a draft and there is a template set
            if (buttonName != 'submit-save' && $containerDiv.find('#compose-email-template').length) {
                templateContent = $containerDiv.find('#compose-email-template')[0].innerHTML;

                // Remove email template div and resize div and only keep user typed text
                $containerDiv.find('#compose-email-template').remove();
            }

            $containerDiv.find('#resize-div').remove();

            /**
             * You'd expect HLInbox.getEditor().setValue or $('#id_body_html').html
             * would work to set the value of the textarea.
             * Sadly they don't, which is why .val is used
             */
            $('#id_body_html').val(templateContent + '<br>' + $containerDiv[0].innerHTML);

            // Make sure both buttons of the same name are set to the loading state
            $('button[name="' + buttonName + '"]').button('loading');

            // No validation needed, remove attachments to prevent unneeded uploading.
            $('[id|=id_attachments]:file').filter(function () {
                return $(this).data('formset-disabled') == true;
            }).remove();

            Metronic.blockUI($('.inbox-content'), false, '');

            $form.submit();
        },
        handleInboxComposeSubmit: function (inboxCompose, event) {
            event.preventDefault();

            var buttonName = $(inboxCompose).attr('name'),
                $form = $($(inboxCompose).closest('form'));

            if (buttonName == 'submit-save') {
                var draftPk = $('#id_draft_pk').val();
                // If we are saving a (existing) draft, change url
                if(draftPk) {
                    $form.attr('action', '/messaging/email/draft/' + draftPk + '/');
                } else {
                    $form.attr('action', '/messaging/email/draft/');
                }
            }
            HLInbox.submitForm(buttonName, $form);
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

            if (emailAccountId) {
                var url = self.config.defaultEmailTemplateUrl + emailAccountId + '/';

                $.getJSON(url, function(data) {
                    $(self.config.templateField).select2('val', data['template_id']).change();
                });
            }
            else {
                toastr.error('Sorry, I couldn\'t load your default email template. You could try reloading the page');
            }
        },

        setNewEditorValue: function (data, templateChanged) {
            var self = this;
            var htmlPart = data['template'];
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
                        changeTemplate = confirm(self.config.overwriteTemplateConfirm);
                    }
                    else {
                        // Template wasn't changed, so a new recipient was entered
                        changeTemplate = true;
                    }

                    if (changeTemplate) {
                        var addedTemplateText = '';

                        if (self.config.currentTemplate) {
                            var diff = {};

                            // First time changing a draft needs a different operation
                            // We want to check if the draft template differs from the default
                            if (self.config.messageType == 'draft' && htmlPart == self.config.currentTemplate) {
                                diff = JsDiff.diffChars(currentTemplate.html(), htmlPart);
                            }
                            else {
                                // Otherwise compare the current editor value with the current template
                                diff = JsDiff.diffChars(currentTemplate.html(), self.config.currentTemplate);
                            }

                            diff.forEach(function (part) {
                                // Get all text that was changed/added
                                if (part.added || part.removed) {
                                    addedTemplateText += part.value;
                                }
                            });
                        }

                        self.config.currentTemplate = htmlPart;

                        // Change the html of the existing email template and add text that was added to the template
                        currentTemplate.html(htmlPart + addedTemplateText);
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

                self.config.currentTemplate = htmlPart;
            }

            // Only overwrite the subject if a new email is being created
            if (this.config.messageType === 'new' && data['template_subject'] != '') {
                $('#id_subject').val(data['template_subject']);
            }

            if (newEditorValue.length) {
                editor.setValue(newEditorValue);
                self.resizeEditor();
                self.processAttachments(data['attachments']);
            }
        },

        processAttachments: function (attachments) {
            var cf = this.config;
            // Clear any existing template attachments
            $(cf.templateAttachmentsDiv).empty();

            var attachmentIds = [];

            for (var i = 0; i < attachments.length; i++) {
                var attachment = attachments[i];

                attachmentIds.push(attachment.id);

                var attachmentRow = $(cf.emptyTemplateAttachmentRow).clone();
                attachmentRow.find(cf.templateAttachmentName).html(attachment.name);
                attachmentRow.find(cf.templateAttachmentId).val(attachment.id);
                attachmentRow.removeAttr('id');
                attachmentRow.removeClass('hidden');

                $(cf.templateAttachmentsDiv).append(attachmentRow);
            }

            $(cf.templateAttachmentIds).val(attachmentIds);
        },

        handleTemplateAttachmentsChange: function (attachmentRow) {
            var self = this,
                cf = self.config;

            var rowAttachmentName = attachmentRow.find(cf.templateAttachmentName);

            if (rowAttachmentName.hasClass('mark-deleted')) {
                rowAttachmentName.removeClass('mark-deleted');
            }
            else {
                rowAttachmentName.addClass('mark-deleted');
            }

            attachmentRow.find('[data-formset-delete-button]').toggleClass('hidden');
            attachmentRow.find('[data-formset-undo-delete]').toggleClass('hidden');

            var newAttachmentIds = [];

            var attachments = $(cf.templateAttachmentRow);
            attachments.each(function () {
                if (!$(this).find(cf.templateAttachmentName).hasClass('mark-deleted')) {
                    var attachmentId = $(this).find(cf.templateAttachmentId).val();
                    if (attachmentId !== "") {
                        // Make sure the value of the empty attachment row doesn't get added
                        newAttachmentIds.push(attachmentId);
                    }
                }
            });

            $(cf.templateAttachmentIds).val(newAttachmentIds);
        },

        setSuccesURL: function(previousState){
            if(previousState != null){
                $("input[name='success_url']").val(previousState);
            }
        }
    }
})(jQuery, window, document);

})(angular);
(function(angular){
'use strict';
(function($, window, document, undefined){
    window.HLFormsets = {
        config: {
            formsetClass: '.formset'
        },
        init: function (config) {
            var self = this;
            // Setup configuration
            if ($.isPlainObject(config)) {
                $.extend(self.config, config);
            }

            $(self.config.formsetClass).formset();
            self.initListeners();
        },

        initListeners: function() {
            var self = this;
            var body = $('body');

            body.on('formAdded', '[data-formset-form]', function() {
                var formset_element = $(this).parents('.formset');
                var add_element = $(formset_element).find('.add-link');

                var indent = ($(formset_element).attr('data-formset-indent') || 'true') == 'true';
                if(indent) {
                    $(add_element).find('.form-control-static').addClass('col-md-offset-2').removeClass('form-control-static');
                }
                $(add_element).find('label').addClass('hide');

                if ($(formset_element).find('[data-formset-form]').length === 1) {
                    $(this).find('label.hide').removeClass('hide');

                    if(indent) {
                        $(this).find('.field_wrapper').removeClass('col-md-offset-2');
                    }
                }
                HLSelect2.init();
            });

            body.on('formDeleted', '[data-formset-form]', function() {
                $(this).stop().slideDown();
                $(this).find(':input:enabled:visible').attr('data-formset-disabled', true).attr('readonly', 'readonly');
                $(this).find('[data-formset-delete-button]').toggleClass('hidden');
                $(this).find('[data-formset-undo-delete]').toggleClass('hidden');
            });

            body.on('click', '[data-formset-form] [data-formset-undo-delete]', function() {
                var formset = $(this).closest('[data-formset-form]');

                formset.find('[data-formset-disabled=true]').removeAttr('data-formset-disabled').removeAttr('readonly');
                formset.find('input[name$="DELETE"]').attr('checked', false).change();
                formset.find('[data-formset-delete-button]').toggleClass('hidden');
                $(this).toggleClass('hidden');
            });

        }
    }
})(jQuery, window, document);

})(angular);
(function(angular){
'use strict';
(function($, window, document, undefined){
    window.HLSelect2 = {
        config: {
            tagInputs: 'input.tags',
            ajaxInputs: 'input.select2ajax',
            tagsAjaxClass: 'tags-ajax',
            ajaxPageLimit: 30,
            clearText: '-- Clear --'
        },

        init: function( config ) {
            var self = this;
            // Setup configuration
            if ($.isPlainObject(config)) {
                $.extend(self.config, config);
            }
            // On initialize, setup select2
            self.setupSelect2();
            self.initListeners();
        },

        initListeners: function() {
            var self = this;
            // When modal is shown, lets instantiate the select2 in the modals
            $(document).on('shown.bs.modal', '.modal', function() {
                self.setupSelect2();
            });
        },

        setupSelect2: function() {
            // Setup select2 for non-ajaxified selects, ajaxified selects
            // are using hidden inputs.
            $('select').select2({
                // at least this many results are needed to enable the search field
                // (9 is the amount at which the user must scroll to see all items)
                minimumResultsForSearch: 9
            });
            this.createTagInputs();
            this.createAjaxInputs();
        },

        createTagInputs: function() {
            // Setup tag inputs
            $(this.config.tagInputs).each(function() {
                if (!$(this).data().hasOwnProperty('select2')) {
                    var tags = [];
                    var $this = $(this);
                    if ($this.data('choices')) {
                        tags = $this.data('choices').split(',');
                    }
                    $this.select2({
                        tags: tags,
                        tokenSeparators: [',', ' '],
                        width: '100%'
                    });
                }
            });
        },

        createAjaxInputs: function() {
            // Setup inputs that needs remote link
            var self = this;
            var cf = self.config;

            $(cf.ajaxInputs).each(function() {
                var $this = $(this);
                var _data = $this.data();
                // _data.tags is a marker for AjaxSelect2Widget which indicates
                // that it expects multiple values as input.

                // Prevent Select2 from being initialized on elements that already have Select2
                if (!_data.hasOwnProperty('select2')) {
                    var options = {
                        ajax: {
                            cache: true,
                            data: function (term, page) {
                                // page is the one-based page number tracked by Select2
                                var data = null;

                                if ($this.hasClass(cf.tagsAjaxClass) && !_data.tags) {
                                    if (term === '') {
                                        // elasticsearch breaks when the term is empty, so just look for non-empty results
                                        term = '*';
                                    }
                                    // search for contacts and accounts containing the search term, but only those with an email address
                                    var filterQuery = '((_type:contacts_contact AND (name:' + term + ' OR email_addresses.email_address:' + term + ')) ' +
                                        'OR (_type:accounts_account AND (name:' + term + ' OR email_addresses.email_address:' + term + '))) ' +
                                        'AND email_addresses.email_address:*';

                                    data = {
                                        filterquery: filterQuery,
                                        size: cf.ajaxPageLimit, // page size
                                        page: (page - 1), // page number, zero-based
                                        sort: '-modified' //sort modified descending
                                    };
                                }
                                else {
                                    var term_stripped = term.trim();
                                    data = {
                                        filterquery: term_stripped ? 'name:('+term_stripped+')' : '', //search term
                                        size: cf.ajaxPageLimit, // page size
                                        page: (page - 1), // page number, zero-based
                                        sort: '-modified' //sort modified descending
                                    };
                                }

                                var filters = $this.data('filter-on');
                                if (typeof filters !== 'undefined' && filters !== '') {
                                    filters.split(',').forEach(function (filter) {
                                        if (filter.indexOf('id_') === 0) {
                                            var filter_val = $('#' + filter).val();
                                            var filter_name = filter.substring(3);
                                            if (filter_name.indexOf('case_quickbutton_') === 0) {
                                                filter_name = filter.substring(20);
                                            } else if (filter_name == 'account') {
                                                // This is a special case at the moment, in the future we might have
                                                // more cases like this.
                                                // But for now, just do this check
                                                filter_name = 'accounts.id';
                                            }
                                            if (filter_val && filter_val > 0) {
                                                data.filterquery += ' ' + filter_name + ':' + filter_val;
                                            }
                                        } else {
                                            data.type = filter;
                                        }
                                    });
                                }

                                return data;
                            },

                            results: function (data, page) {
                                var more = (page * cf.ajaxPageLimit) < data.total; // whether or not there are more results available

                                if ($this.hasClass(cf.tagsAjaxClass) && !_data.tags) {
                                    var parsed_data = [];

                                    data.hits.forEach(function (hit) {
                                        // Only display contacts with an e-mail address
                                        for (var i = 0; i < hit.email_addresses.length; i++) {
                                            // The text which is actually used in the application
                                            var used_text = '"' + hit.name + '" <' + hit.email_addresses[i].email_address + '>';
                                            // The displayed text
                                            var displayed_text = hit.name + ' <' + hit.email_addresses[i].email_address + '>';
                                            // Select2 sends 'id' as the value, but we want to use the email
                                            // So store the actual id (hit.id) under a different name
                                            parsed_data.push({id: used_text, text: displayed_text, object_id: hit.id});
                                        }
                                    });

                                    // Array elements with empty text can't be added to select2, so manually fill a new array
                                    data.hits = parsed_data;
                                }
                                else {
                                    data.hits.forEach(function (hit) {
                                        hit.text = hit.name;
                                    });
                                }

                                // Add clear option, but not for multiple select2.
                                if ((page == 1 && !$this.hasClass(cf.tagsAjaxClass)) && !_data.tags) {
                                    data.hits.unshift({id: -1, text:cf.clearText});
                                }
                                return {
                                    results: data.hits,
                                    more: more
                                };
                            }
                        },

                        initSelection: function (item, callback) {
                            var id = item.val();
                            var text = item.data('selected-text');
                            var data = { id: id, text: text };
                            callback(data);
                        }
                    };

                    if ($this.hasClass(cf.tagsAjaxClass)) {
                        options.tags = true;
                        options.tokenSeparators = [',', ' '];
                        // Create a new tag if there were no results
                        options.createSearchChoice = function (term, data) {
                            if ($(data).filter(function () {
                                    return this.text.localeCompare(term) === 0;
                                }).length === 0) {
                                return {
                                    id: term,
                                    text: term
                                };
                            }
                        };
                        // Prevent select2 dropdown from opening when pressing enter
                        options.openOnEnter = false;
                    }

                    // Set select2 to multiple.
                    if(_data.tags) {
                        options.tags = true;
                        options.multiple = true;
                    }


                    $this.select2(options);
                    // Set the initial form value from a JSON encoded data attribute called data-initial
                    if(_data.tags) {
                        $this.select2('data', _data.initial);
                    }
                }
            });
        }
    };

})(jQuery, window, document);

})(angular);
(function(angular){
'use strict';
(function($, window, document, undefined){
    window.HLShowAndHide = {
        config: {
            selector: '.show-and-hide-input'
        },

        init: function( config ) {
            var self = this;
            // Setup configuration
            if ($.isPlainObject(config)) {
                $.extend(self.config, config);
            }
            // On initialize, setup show and hide
            self.initListeners();
        },

        initListeners: function() {
            var self = this;

            // When modal is shown, lets instantiate the select2 in the modals
            $('body').on('click', '.form .toggle-original-form-input', function() {
                var field = $(this).closest('.show-and-hide-input');

                /* hide clicked link */
                $(this).parent().addClass('hide');

                /* toggle form input */
                if($(this).data('action') == 'show') {
                    /* show the other link */
                    $(field).find('[data-action="hide"]').parent().removeClass('hide');

                    /* show the form input */
                    $(field).find('.original-form-widget').removeClass('hide');

                    /* (re)enable fields */
                    $(field).find(':input').removeAttr('disabled');

                    var input = $(field).find(':input:visible:not([type="file"]):first');
                    if(input) {
                        /* adding to the end of the execution queue reliably sets the focus */
                        /*  e.g. without, this only works once for select2 inputs */
                        setTimeout(function() {
                            // setCaretAtEnd(input);
                        }, 0);
                    }
                } else if($(this).data('action') == 'hide') {
                    /* show the other link */
                    $(field).find('[data-action="show"]').parent().removeClass('hide');

                    /* hide the form input */
                    $(field).find('.original-form-widget').addClass('hide');

                    /* disabled fields will not be posted */
                    $(field).find(':input').attr('disabled', 'disabled');
                }
            });
        }
    };

})(jQuery, window, document);

})(angular);
(function(angular){
'use strict';
(function($, window, document, undefined) {
    window.HLDataProvider = {
        config: {
            buttonDataProvider: ':button.dataprovider',
            loadingText: 'Beaming up the information now, almost within range!',
            loadingHeader: 'I\'m on my way!',
            provideUrl: '/provide/account/',
            dataProviderClass: '.dataprovider',
            errorHeader: 'Oops!',
            errorText: 'There was an error trying to fetch your data, please don\'t be mad.',
            successHeader: 'Yeah!',
            successText: 'We did it! Your new data should be right there waiting for you.',
            hiddenSuccessHeader: 'Psst!',
            hiddenSuccessText: 'Did you know I did more work in the background? ;)',
            overwriteConfirmHeader: 'Do you wish to overwrite the following fields?\n',
            fields: [
                'name',
                'description',
                'legalentity',
                'taxnumber',
                'bankaccountnumber',
                'cocnumber',
                'iban',
                'bic',
            ],
            formsets: [
                'email_addresses',
                'phone_numbers',
                'addresses'
            ]
        },

        init: function(config) {
            // Setup config
            var self = this;
            if ($.isPlainObject(config)) {
                $.extend(self.config, config);
            }

            self.initListeners();
        },

        initListeners: function() {
            var self = this,
                cf = self.config;

            $('body').on('click', cf.buttonDataProvider, function(event) {
                // On button press
                self.findDataProviderInfo.call(self, this, event);
            }).on('keydown', 'div' + cf.dataProviderClass + ' > input', function(event) {
                // Catch ENTER on Dataprovider input
                if (event.which === 13) {
                    self.findDataProviderInfo.call(self, cf.buttonDataProvider, event);
                    // Prevent form submission
                    event.preventDefault();
                }
            });
        },

        findDataProviderInfo: function(button, event) {
            var self = this,
                cf = self.config,
                $button = $(button),
                $form = $button.closest('form'),
                $input = $('div' + cf.dataProviderClass +' > input'),
                domain = self.sanitizeDomain($input.val());

            // Show busy gui to user
            $button.button('loading');
            toastr.info(cf.loadingText, cf.loadingHeader);

            var url = cf.provideUrl + domain;
            $.getJSON(url)
                .done(function(data) {
                    if (data.error) {
                        toastr.error(data.error.message, cf.errorHeader);
                    } else {
                        self.fillForm($form, data, cf.fields, cf.formsets);
                        toastr.success(cf.successText, cf.successHeader);
                    }
                })
                .fail(function() {
                    toastr.error(cf.errorText, cf.errorHeader);
                })
                .always(function() {
                    $button.button('reset');
                });

            event.preventDefault();
        },

        sanitizeDomain: function(url) {
            var domain = $.trim(url.replace('http://', ''));
            domain = $.trim(domain.replace('https://', ''));
            // Always add last '/'
            if (domain.slice(-1) !== '/') {
                domain += '/';
            }
            return domain;
        },

        fillForm: function($form, data, fields, formsets) {
            var self = this,
                cf = self.config;

            var checkOverwrite = self.loopTroughFields(fields, $form, data),
                checkOverwriteFields = checkOverwrite[0],
                checkOverwriteLabels = checkOverwrite[1];

            // Check if there are fields for which we need to do an overwrite check
            if (checkOverwriteFields.length) {
                // Ask the user whether to overwrite or not
                if (confirm(cf.overwriteConfirmHeader + checkOverwriteLabels.join('\n'))) {
                    // Loop through fields that need to be overwritten
                    checkOverwriteFields.forEach(function(field) {
                        var $input = $form.find('[name="' + field + '"]');
                        self.fillField($input, data[field]);
                    });
                }
            }

            // Loop through formsets
            self.loopTroughFormSets(formsets, $form, data);

        },

        loopTroughFields: function(fields, $form, data) {
            var self = this,
                cf = self.config,
                checkOverwriteFields = [],
                checkOverwriteLabels = [],
                filledHiddenField = false;

            // Loop through all fields
            fields.forEach(function(field) {
                // Input is the field in the current form
                var $input = $form.find('[name="' + field + '"]');
                // Always clear the field if it's hidden
                if ($input.attr('type') == 'hidden' || $input.parent().hasClass('hide')) {
                    $input.val('');
                    if (data[field]) {
                        filledHiddenField = true;
                    }
                }
                // Check if there is data for the field, else do nothing
                if (data[field]) {
                    // Check if the field does not exist in the current form
                    if ($input.val() !== undefined) {
                        // Check if the field has a value and that value is not the field placeholder
                        if ($input.val().length && $input.val() !== $input.attr('placeholder')) {
                            // Display label of field instead of field name
                            var label = $input.parents('.form-group').find('label').text();
                            // Field is not empty, check before overwrite
                            checkOverwriteFields.push(field);
                            checkOverwriteLabels.push('- ' + label);
                        } else {
                            // Field is empty, fill it with new data
                            self.fillField($input, data[field]);
                        }
                    }
                }
            });

            if (filledHiddenField) {
                toastr.success(cf.hiddenSuccessText, cf.hiddenSuccessHeader);
            }

            return [checkOverwriteFields, checkOverwriteLabels];
        },

        loopTroughFormSets: function(formsets, $form, data){
            for (var i=0; i < formsets.length; i++) {
                var formset = formsets[i];
                // Check if there is data for the formset
                if (data[formset] && data[formset].length) {
                    var $formsetDiv = $form.find('#' + formset),
                        $formsetAddLink = $formsetDiv.find('[data-formset-add]'),
                        newFormsets = data[formset],
                        $foundInput;

                    for (var j = 0; j < newFormsets.length; j++) {
                        var newFormset = newFormsets[j],
                            insertNewFormset = false,
                            $newElement;

                        if (typeof newFormset === 'object') {
                            var key,
                                hasFoundInput = false;
                            for (key in newFormset) {
                                $foundInput = $formsetDiv.find(':input[name$="' + key +'"]');
                                if ($foundInput.length){
                                    hasFoundInput = true;
                                    $foundInput = $foundInput.filter(function () {
                                        var val = $(this).val(),
                                            newVal = newFormset[key];

                                        return ((val === '' && newVal === null) || val == newVal);
                                    });
                                    if (!$foundInput.length) {
                                        // One of the values is different so we need to add a new formset
                                        insertNewFormset = true;
                                    }
                                }
                            }
                            if (insertNewFormset || !hasFoundInput) {
                                $formsetAddLink.click();
                                $newElement =  $formsetDiv.find('[data-formset-body] [data-formset-form]:last');
                                for (key in newFormset) {
                                    $newElement.find(':input[name$="' + key +'"]').val(newFormset[key]);
                                }
                            }
                        } else if (typeof newFormset === 'string') {
                            $foundInput = $formsetDiv.find(':input').filter(function () {
                                return $(this).val() == newFormset;
                            });
                            if (!$foundInput.length) {
                                $formsetAddLink.click();
                                $newElement =  $formsetDiv.find('[data-formset-body] [data-formset-form]:last');
                                $newElement.find(':input:first').val(newFormset);
                            }
                        }
                    }
                }
            }
        },

        fillField: function($input, value) {
            if (typeof value === 'string') {
                // String
                $input.val(value);
            } else if (typeof value[0] === 'string') {
                // List of strings
                var uniqueValues = value.concat($input.val().split(',')).filter(function(val, index, self) {
                    return (self.indexOf(val) === index) && (val !== '');
                });
                $input.val(uniqueValues.join());
            } else {
                // JSON object
                $input.val(JSON.stringify(value));
            }
            $input.change();
            if ($input.parent().hasClass('original-form-widget') && $input.parent().hasClass('hide')) {
                // show the input, by reusing the click handler as defined in the utils.
                $input.parents(".show-and-hide-input").find('a[data-action="show"]').trigger('click');
            }
        }
    }
})(jQuery, window, document);

})(angular);
(function(angular){
'use strict';
var $body = $('body');
$body.on('blur', 'input[name^="phone"]', function() {
    // Format telephone number
    var $phoneNumberInput = $(this);
    var phone = $phoneNumberInput.val();
    if (phone.match(/[a-z]|[A-Z]/)) {
        // if letters are found, skip formatting: it may not be a phone field after all
        return false;
    }

    // Match on mobile phone nrs e.g. +316 or 06, so we can automatically set the type to mobile.
    if (phone.match(/^\+316|^06/)) {
        var typeId = $phoneNumberInput.attr('id').replace('raw_input', 'type');
        $('#' + typeId).select2('val', 'mobile');
    }

    phone = phone
        .replace("(0)","")
        .replace(/\s|\(|\-|\)|\.|\\|\/|\–|x|:|\*/g, "")
        .replace(/^00/,"+");

    if (phone.length == 0) {
        return false;
    }

    if (!phone.startsWith('+')) {
        if (phone.startsWith('0')) {
            phone = phone.substring(1);
        }
        phone = '+31' + phone;
    }

    if (phone.startsWith('+310')) {
        phone = '+31' + phone.substring(4);
    }
    $phoneNumberInput.val(phone);
});

$body.on('change', 'select[id*="is_primary"]', function(e) {
    if($(e.currentTarget).val() == 'True'){
        $('select[id*="is_primary"]').each(function(i){
            if($(this).is('select') && $(this).val() == 'True'){
                $(this).val('False');
            }
        });
        $(e.currentTarget).val('True');
        HLSelect2.init();
    }
});

function addBusinessDays(date, businessDays) {
    var weeks = Math.floor(businessDays/5);
    var days = businessDays % 5;
    var day = date.getDay();
    if (day === 6 && days > -1) {
       if (days === 0) {days-=2; day+=2;}
       days++; dy -= 6;}
    if (day === 0 && days < 1) {
       if (days === 0) {days+=2; day-=2;}
       days--; day += 6;}
    if (day + days > 5) days += 2;
    if (day + days < 1) days -= 2;
    date.setDate(date.getDate() + weeks * 7 + days);
    return date;
}

})(angular);
(function(angular){
'use strict';
/**
 * Router definition.
 */
angular.module('app.accounts').config(accountConfig);

accountConfig.$inject = ['$stateProvider'];
function accountConfig ($stateProvider) {

    $stateProvider.state('base.accounts.detail.delete', {
        url: '/delete',
        views: {
            '@': {
                controller: 'AccountDeleteController'
            }
        }
    });
}

/**
 * Controller to delete a account
 */
angular.module('app.accounts').controller('AccountDeleteController', AccountDeleteController);

AccountDeleteController.$inject = ['$state', '$stateParams', 'Account'];
function AccountDeleteController ($state, $stateParams, Account) {
    var id = $stateParams.id;

    Account.delete({
        id:id
    }, function() {  // On success
        $state.go('base.accounts');
    }, function(error) {  // On error
        // Error notification needed
        $state.go('base.accounts');
    });
}

})(angular);
(function(angular){
'use strict';
/**
 * Router definition.
 */
angular.module('app.accounts').config(accountConfig);

accountConfig.$inject = ['$stateProvider'];
function accountConfig ($stateProvider) {
    $stateProvider.state('base.accounts.detail', {
        url: '/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'accounts/controllers/detail.html',
                controller: AccountDetailController
            }
        },
        ncyBreadcrumb: {
            label: '{{ account.name }}'
        },
        resolve: {
            account: ['AccountDetail', '$stateParams', function(AccountDetail, $stateParams) {
                var accountId = $stateParams.id;
                return AccountDetail.get({id: accountId}).$promise
            }]
        }
    })
}

angular.module('app.accounts').controller('AccountDetailController', AccountDetailController);

AccountDetailController.$inject = ['$scope', '$stateParams', 'CaseDetail', 'ContactDetail', 'DealDetail', 'account'];
function AccountDetailController($scope, $stateParams, CaseDetail, ContactDetail, DealDetail, account) {
    /**
     * Details page with historylist and more detailed account information.
     */
    var id = $stateParams.id;

    $scope.account = account;
    $scope.conf.pageTitleBig = account.name;
    $scope.conf.pageTitleSmall = 'change is natural';

    $scope.caseList = CaseDetail.query({filterquery: 'account:' + id});
    $scope.caseList.$promise.then(function(caseList) {
        $scope.caseList = caseList;
    });

    $scope.dealList = DealDetail.query({filterquery: 'account:' + id});
    $scope.dealList.$promise.then(function(dealList) {
        $scope.dealList = dealList;
    });

    $scope.contactList = ContactDetail.query({filterquery: 'accounts.id:' + id});
    $scope.contactList.$promise.then(function(contactList) {
        $scope.contactList = contactList;
    });
}

})(angular);
(function(angular){
'use strict';
/**
 * Router definition.
 */
angular.module('app.accounts').config(accountConfig);

accountConfig.$inject = ['$stateProvider'];
function accountConfig ($stateProvider) {
    $stateProvider.state('base.accounts', {
        url: '/accounts',
        views: {
            '@': {
                templateUrl: 'accounts/controllers/list.html',
                controller: AccountList,
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: 'Accounts'
        }
    });
}

/**
 * AccountList is a controller to show list of contacts
 *
 */
angular.module('app.accounts').controller('AccountList', AccountList);

AccountList.$inject = ['$scope', '$window', 'Account', 'Cookie'];
function AccountList ($scope, $window, Account, Cookie) {
    var vm = this;
    var cookie = Cookie('accountList');
    /**
     * table object: stores all the information to correctly display the table
     */
    vm.table = {
        page: 1,  // current page of pagination: 1-index
        pageSize: 20,  // number of items per page
        totalItems: 0, // total number of items
        filter: cookie.get('filter', ''),  // search filter
        order:  cookie.get('order', {
            ascending: true,
            column:  'modified'  // string: current sorted column
        }),
        visibility: cookie.get('visibility', {
            name: true,
            contactInformation: true,
            assignedTo: true,
            created: true,
            modified: true,
            tags: true,
            customerId: true
        })
    };
    vm.deleteAccount = deleteAccount;
    vm.setFilter = setFilter;
    vm.exportToCsv = exportToCsv;

    activate();

    /////////////

    function activate() {
        _setupWatches();
    }

    $scope.conf.pageTitleBig = 'Accounts';
    $scope.conf.pageTitleSmall = 'An overview of accounts';


    function deleteAccount (account) {
        if (confirm('Are you sure?')) {
            Account.delete({
                id:account.id
            }, function() {  // On success
                var index = vm.table.items.indexOf(account);
                vm.table.items.splice(index, 1);
            }, function(error) {  // On error
                alert('something went wrong.')
            })
        }
    }

    /**
     * _updateTableSettings() sets scope variables to the cookie
     */
    function _updateTableSettings() {
        cookie.put('filter', vm.table.filter);
        cookie.put('order', vm.table.order);
        cookie.put('visibility', vm.table.visibility);
    }

    /**
     * _updateAccounts() reloads the accounts through a service
     *
     * Updates table.items and table.totalItems
     */
    function _updateAccounts() {
        Account.getAccounts(
            vm.table.filter,
            vm.table.page,
            vm.table.pageSize,
            vm.table.order.column,
            vm.table.order.ascending
        ).then(function(data) {
                vm.table.items = data.accounts;
                vm.table.totalItems = data.total;
            }
        );
    }

    function _setupWatches() {
        /**
         * Watches the model info from the table that, when changed,
         * needs a new set of accounts
         */
        $scope.$watchGroup(['vm.table.page', 'vm.table.order.column', 'vm.table.order.ascending', 'vm.table.filter'], function() {
            _updateTableSettings();
            _updateAccounts();
        });

        /**
         * Watches the model info from the table that, when changed,
         * needs to store the info to the cache
         */
        $scope.$watchCollection('vm.table.visibility', function() {
            _updateTableSettings();
        });
    }


    /**
     * setFilter() sets the filter of the table
     *
     * @param queryString string: string that will be set as the new filter on the table
     */
    function setFilter (queryString) {
        vm.table.filter = queryString;
    }

    /**
     * exportToCsv() creates an export link and opens it
     */
    function exportToCsv () {
        var getParams = '';
        // If there is a filter, add it
        if (vm.table.filter) {
            getParams += '&export_filter=' + vm.table.filter;
        }

        // Add all visible columns
        angular.forEach(vm.table.visibility, function(value, key) {
            if (value) {
                getParams += '&export_columns='+ key;
            }
        });

        // Setup url
        var url = '/accounts/export/';
        if (getParams) {
            url += '?' + getParams.substr(1);
        }

        $window.open(url);
    }
}

})(angular);
(function(angular){
'use strict';
/**
 * Router definition.
 */
angular.module('app.accounts').config(accountConfig);

accountConfig.$inject = ['$stateProvider'];
function accountConfig ($stateProvider) {
    $stateProvider.state('base.accounts.create', {
        url: '/create',
        views: {
            '@': {
                templateUrl: '/accounts/create/',
                controller: 'AccountUpsertController'
            }
        },
        ncyBreadcrumb: {
            label: 'Create'
        }
    });

    $stateProvider.state('base.accounts.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: function(elem) {
                    return '/accounts/' + elem.id + '/edit/';
                },
                controller: 'AccountUpsertController'
            }
        },
        ncyBreadcrumb: {
            label: 'Edit'
        }
    });
}

/**
 * Controller for update and new Account actions.
 */
angular.module('app.accounts').controller('AccountUpsertController', AccountUpsertController);

AccountUpsertController.$inject = ['$scope', '$stateParams', 'AccountDetail'];
function AccountUpsertController ($scope, $stateParams, AccountDetail) {
    var id = $stateParams.id;
    // New Account; set title.
    if(!id) {
        $scope.conf.pageTitleBig = 'New Account';
        $scope.conf.pageTitleSmall = 'change is natural';
    } else {
        // Existing Account; Get details from ES and set title.
        var accountPromise = AccountDetail.get({id: id}).$promise;
        accountPromise.then(function(account) {
            $scope.account = account;
            $scope.conf.pageTitleBig = account.name;
            $scope.conf.pageTitleSmall = 'change is natural';
            HLSelect2.init();
        });
    }
    HLDataProvider.init();
    HLFormsets.init();
}

})(angular);
(function(angular){
'use strict';
/**
 * Account detail widget
 */
angular.module('app.accounts.directives').directive('accountDetailWidget', AccountDetailWidget);

function AccountDetailWidget() {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            account: '=',
            height: '='
        },
        templateUrl: 'accounts/directives/detail_widget.html'
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.accounts.services').factory('Account', Account);

Account.$inject = ['$filter', '$http', '$resource'];
function Account ($filter, $http, $resource) {
    var Account = $resource(
        '/api/accounts/account/:id',
        null,
        {
            update: {
                method: 'PUT',
                params: {
                    id: '@id'
                }
            },
            delete:  {
                method: 'DELETE'
            }
        });

    Account.getAccounts = getAccounts;
    Account.prototype.getEmailAddress = getEmailAddress;

    //////

    /**
     * getAccounts() gets the accounts from the search backend through a promise
     *
     * @param queryString string: current filter on the accountlist
     * @param page int: current page of pagination
     * @param pageSize int: current page size of pagination
     * @param orderColumn string: current sorting of accounts
     * @param orderedAsc {boolean}: current ordering
     *
     * @returns Promise object: when promise is completed:
     *      {
     *          accounts list: paginated account objects
     *          total int: total number of account objects
     *      }
     */
    function getAccounts (queryString, page, pageSize, orderColumn, orderedAsc) {

        var sort = '';
        if (orderedAsc) sort += '-';
        sort += orderColumn;

        return $http({
            url: '/search/search/',
            method: 'GET',
            params: {
                type: 'accounts_account',
                q: queryString,
                page: page - 1,
                size: pageSize,
                sort: sort
            }
        })
            .then(function(response) {
                return {
                    accounts: response.data.hits,
                    total: response.data.total
                };
            });
    }

    function getEmailAddress() {
        var account = this;

        var primaryEmails = $filter('filter')(account.email_addresses, {status: 2});

        if (primaryEmails.length) {
            return primaryEmails[0];
        } else if (account.email_addresses.length) {
            return account.email_addresses[0];
        }
    }
    return Account;
}

})(angular);
(function(angular){
'use strict';
angular.module('app.accounts.services').factory('AccountDetail', AccountDetail);

AccountDetail.$inject = ['$resource'];
function AccountDetail ($resource) {
    function getPhone(account) {
        if (account.phone_mobile) return account.phone_mobile[0];
        if (account.phone_work) return account.phone_work[0];
        if (account.phone_other) return account.phone_other[0];
        return '';
    }
    function getPhones(account) {
        var phones = [];
        if (account.phone_mobile) phones = phones.concat(account.phone_mobile);
        if (account.phone_work) phones = phones.concat(account.phone_work);
        if (account.phone_other) phones = phones.concat(account.phone_other);
        return phones;
    }
    return $resource(
        '/search/search/?type=accounts_account&filterquery=id\::id',
        {},
        {
            get: {
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    if (data && data.hits && data.hits.length > 0) {
                        var account = data.hits[0];
                        account.phone = getPhone(account);
                        account.phones = getPhones(account);
                        return account;
                    }
                    return null;
                }
            }
        }
    );
}

})(angular);
(function(angular){
'use strict';
angular.module('app.base').config(appConfig);

appConfig.$inject = ['$stateProvider'];
function appConfig ($stateProvider) {
    $stateProvider.state('base', {
        abstract: true,
        controller: BaseController,
        ncyBreadcrumb: {
            label: 'Lily'
        }
    });
}

angular.module('app.base').controller('BaseController', BaseController);

BaseController.$inject = ['$scope', '$state', 'Notifications'];
function BaseController ($scope, $state, Notifications) {
    $scope.conf = {
        headTitle: 'Welcome!',
        pageTitleBig: 'HelloLily',
        pageTitleSmall: 'welcome to my humble abode!'
    };

    $scope.loadNotifications = loadNotifications;

    activate();

    //////////

    function activate(){
        $scope.$on('$stateChangeSuccess', _setPreviousState);
        $scope.$on('$viewContentLoaded', _contentLoadedActions);
    }

    function loadNotifications() {
        Notifications.query(function(notifications) {  // On success
            angular.forEach(notifications, function(message) {
                toastr[message.level](message.message);
            });
        }, function(error) {  // On error
            console.log('error!');
            console.log(error);
        })
    }

    function _contentLoadedActions() {
        Metronic.initComponents(); // init core components
        HLSelect2.init();
        HLFormsets.init();
        HLShowAndHide.init();
        autosize($('textarea'));

        $scope.loadNotifications();
    }

    function _setPreviousState(event, toState, toParams, fromState, fromParams){
        $scope.previousState = $state.href(fromState, fromParams);
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.base').controller('headerController', headerController);

headerController.$inject = ['$scope'];
function headerController ($scope) {
    $scope.$on('$includeContentLoaded', function() {
        Layout.initHeader(); // init header
    });
}

})(angular);
(function(angular){
'use strict';
angular.module('app.base').controller('sidebarController', sidebarController);

sidebarController.$inject = ['$scope'];
function sidebarController ($scope) {
    $scope.$on('$includeContentLoaded', function() {
        Layout.initSidebar(); // init sidebar
    });
}

})(angular);
(function(angular){
'use strict';
/**
 * checkbox Directive makes a nice uniform checkbox and binds to a model
 *
 * @param model object: model to bind checkbox with
 *
 * Example:
 * <checkbox model="table.visibility.name">Name</checkbox>
 */
angular.module('app.directives').directive('checkbox', checkbox);

function checkbox () {
    return {
        restrict: 'E',
        replace: true,
        transclude: true,
        scope: {
            model: '='
        },
        templateUrl: 'base/directives/checkbox.html'
    }
}

})(angular);
(function(angular){
'use strict';
/**
 * Directive give a nice formatting on input elements.
 *
 * It makes sure that the value of the ngModel on the scope has a nice
 * formatting for the user
 */
angular.module('app.directives').directive('dateFormatter', dateFormatter);

dateFormatter.$inject = ['dateFilter'];
function dateFormatter(dateFilter) {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function(scope, element, attrs, ngModel) {
            ngModel.$formatters.push(function(value) {
                if (value) {
                    return dateFilter(value, attrs.dateFormatter);
                }
            })
        }
    }
}

})(angular);
(function(angular){
'use strict';
/**
 * Directive for a confirmation box before the delete in the detail
 * view happens
 */
angular.module('app.directives').directive('detailDelete', detailDelete);

detailDelete.$inject = ['$state'];
function detailDelete ($state) {
    return {
        restrict: 'A',
        link: function (scope, elem, attrs) {

            $(elem).click(function () {
                if (confirm('You are deleting! Are you sure ?')) {
                    $state.go('.delete');
                }
            });
        }
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.directives').directive('resizeIframe', resizeIframe);

function resizeIframe () {
    return {
        restrict: 'A',
        link: function ($scope, element, attrs) {
            var maxHeight = $('body').outerHeight();
            element.on('load', function() {
                element.removeClass('hidden');

                // do this after .inbox-view is visible
                var ifDoc, ifRef = this;

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
                        element.offset().top,
                        $('.footer').outerHeight(),
                        $('.inbox-attached').outerHeight()
                    ];
                    for (var height in subtractHeights) {
                        maxHeight = maxHeight - height;
                    }

                    if (ifDoc.scrollHeight > maxHeight) {
                        ifRef.height = maxHeight;
                    } else {
                        ifRef.height = ifDoc.scrollHeight;
                    }
                }
            });
        }
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.directives').directive('saveAndArchive', saveAndArchiveDirective);

function saveAndArchiveDirective () {
    return {
        restrict: "A",
        link: function(scope, elem, attrs) {

            // Setting button to right text based in archived state
            var $button = $('#archive-button');
            var $archiveField = $('#id_is_archived');
            if ($archiveField.val() === 'True') {
                $button.find('span').text('Save and Unarchive');
            } else {
                $button.find('span').text('Save and Archive');
            }

            // On button click set archived hidden field and submit form
            elem.on('click', function () {
                $button = $('#archive-button');
                $archiveField = $('#id_is_archived');
                var $form = $($button.closest('form').get(0));
                var archive = ($archiveField.val() === 'True' ? 'False' : 'True');
                $archiveField.val(archive);
                $button.button('loading');
                $form.find(':submit').click();
                event.preventDefault();
            });
        }
    }
}

})(angular);
(function(angular){
'use strict';
/**
 * sortColumn Directive adds sorting classes to an DOM element based on `table` object
 *
 * It makes the element clickable and sets the table sorting based on that element
 *
 * @param sortColumn string: name of the column to sort on when clicked
 * @param table object: The object to bind sort column and ordering
 *
 * Example:
 *
 * <th sort-column="last_name" table="table">Name</th>
 *
 * Possible classes:
 * - sorting: Unsorted
 * - sorting_asc: Sorted ascending
 * - sorting_desc: Sorted descending
 */
angular.module('app.directives').directive('sortColumn', sortColumn);

function sortColumn () {
    /**
     * _setSortableIcon() removes current sorting classes and adds new based on current
     * sorting column and direction
     *
     * @param $scope object: current scope
     * @param element object: current DOM element
     * @param sortColumn string: column from current DOM element
     */
    var _setSortableIcon = function($scope, element, sortColumn) {
        // Add classes based on current sorted column
        if($scope.table.order.column === sortColumn) {
            if ($scope.table.order.ascending) {
                $scope.sorted = 1;
            } else {
                $scope.sorted = -1;
            }
        } else {
            $scope.sorted = 0;
        }
    };

    return {
        restrict: 'A',
        scope: {
            table: '='
        },
        transclude: true,
        templateUrl: 'base/directives/sort_column.html',
        link: function ($scope, element, attrs) {
            // Watch the table ordering & sorting
            $scope.$watchCollection('table.order', function() {
                _setSortableIcon($scope, element, attrs.sortColumn);
            });

            // When element is clicked, set the table ordering & sorting based on this DOM element
            element.on('click', function() {
                if($scope.table.order.column === attrs.sortColumn) {
                    $scope.table.order.ascending = !$scope.table.order.ascending;
                    $scope.$apply();
                } else {
                    $scope.table.order.column = attrs.sortColumn;
                    $scope.$apply();
                }
            });
        }
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.directives').directive('ngSpinnerBar', ngSpinnerBar);

ngSpinnerBar.$inject = ['$rootScope'];
function ngSpinnerBar ($rootScope) {
    return {
        link: function(scope, element, attrs) {
            // by defult hide the spinner bar
            element.addClass('hide'); // hide spinner bar by default

            // display the spinner bar whenever the route changes(the content part started loading)
            $rootScope.$on('$stateChangeStart', function() {
                element.removeClass('hide'); // show spinner bar
            });

            // hide the spinner bar on rounte change success(after the content loaded)
            $rootScope.$on('$stateChangeSuccess', function() {
                element.addClass('hide'); // hide spinner bar
                $('body').removeClass('page-on-load'); // remove page loading indicator

                // auto scroll to page top
                setTimeout(function () {
                    Metronic.scrollTop(); // scroll to the top on content load
                }, $rootScope.settings.layout.pageAutoScrollOnLoad);
            });

            // handle errors
            $rootScope.$on('$stateNotFound', function() {
                element.addClass('hide'); // hide spinner bar
            });

            // handle errors
            $rootScope.$on('$stateChangeError', function() {
                element.addClass('hide'); // hide spinner bar
            });
        }
    };
}

})(angular);
(function(angular){
'use strict';
angular.module('app.filters').filter('minValue', minValue);
function minValue () {
    return function(values) {
        values.sort(function(a, b){return a-b});
        return values[0];
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.filters').filter('nl2br', nl2br);

nl2br.$inject = ['$sce'];
function nl2br ($sce) {
    return function(msg,is_xhtml) {
        var is_xhtml = is_xhtml || true;
        var breakTag = (is_xhtml) ? '<br />' : '<br>';
        var msg = (msg + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1'+ breakTag +'$2');
        return $sce.trustAsHtml(msg);
    }
}

})(angular);
(function(angular){
'use strict';
/**
 * relativeDate filter is a filter that represents the date in a nice format
 *
 * relativeDate will return a relative date string given the date. If the
 * date is to far in the past, it will fallback to angulars $filter
 *
 * @param: date {date|string} : date object or date string to transform
 * @param: fallbackDateFormat string (optional): fallback $filter argument
 * @param: compareWithMidnight boolean (optional): should the date comparison be with midnight or not
 *
 * @returns: string : a relative date string
 *
 * usage:
 *
 * {{ '2014-11-19T12:44:15.795312+00:00' | relativeDate }}
 */
angular.module('app.filters').filter('relativeDate', relativeDate);

relativeDate.$inject = ['$filter'];
function relativeDate ($filter) {
    return function (date, fallbackDateFormat, compareWithMidnight) {
        // Get current date
        var now = new Date(),
            calculateDelta, day, delta, hour, minute, week, month, year;

        // If date is a string, format to date object
        if (!(date instanceof Date)) {
            date = new Date(date);
            if (compareWithMidnight) {
                // In certain cases we want to compare with midnight
                date.setHours(23);
                date.setMinutes(59);
                date.setSeconds(59);
            }
        }

        delta = null;
        minute = 60;
        hour = minute * 60;
        day = hour * 24;
        week = day * 7;
        month = day * 30;
        year = day * 365;

        // Calculate delta in seconds
        calculateDelta = function () {
            return delta = Math.round((date - now) / 1000);
        };

        calculateDelta();

        if (delta > day && delta < week) {
            date = new Date(date.getFullYear(), date.getMonth(), date.getDate());
            if (compareWithMidnight) {
                // In certain cases we want to compare with midnight
                date.setHours(23);
                date.setMinutes(59);
                date.setSeconds(59);
            }
            calculateDelta();
        }

        if (!fallbackDateFormat) {
            if (window.innerWidth < 992) {
                // Display as a short version if it's a small screen (tablet, smartphone, etc.)
                fallbackDateFormat = 'dd MMM. yyyy'; // Renders as 29 Jan. 2015
            }
            else {
                fallbackDateFormat = 'dd MMMM yyyy'; // Renders as 29 January 2015
            }
        }

        // Check delta and return result
        if (delta < 0) {
            switch (false) {
                case !(-delta > week):
                    return $filter('date')(date, fallbackDateFormat);
                case !(-delta > day * 2):
                    return '' + -(Math.ceil(delta / day)) + ' days ago';
                case !(-delta > day):
                    return 'yesterday';
                case !(-delta > hour):
                    return '' + -(Math.ceil(delta / hour)) + ' hours ago';
                case !(-delta > minute * 2):
                    return '' + -(Math.ceil(delta / minute)) + ' minutes ago';
                case !(-delta > minute):
                    return 'a minutes ago';
                case !(-delta > 30):
                    return '' + -delta + ' seconds ago';
                default:
                    return 'just now';
            }
        } else {
            switch (false) {
                case !(delta < 30):
                    return 'just now';
                case !(delta < minute):
                    return '' + delta + ' seconds';
                case !(delta < 2 * minute):
                    return 'a minute';
                case !(delta < hour):
                    return '' + (Math.floor(delta / minute)) + ' minutes';
                case Math.floor(delta / hour) !== 1:
                    return 'an hour';
                case !(delta < day):
                    return '' + (Math.floor(delta / hour)) + ' hours';
                case !(delta < day * 2):
                    return 'tomorrow';
                case !(delta < week):
                    return '' + (Math.floor(delta / day)) + ' days';
                case Math.floor(delta / week) !== 1:
                    return 'a week';
                default:
                    // Use angular $filter
                    return $filter('date')(date, fallbackDateFormat);
            }
        }
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.filters').filter('trustAsResourceUrl', trustAsResourceUrl);

trustAsResourceUrl.$inject = ['$sce'];
function trustAsResourceUrl ($sce) {
    return function(val) {
        return $sce.trustAsResourceUrl(val);
    };
}

})(angular);
(function(angular){
'use strict';
/**
 * Cookie Service provides a simple interface to get and store cookie values
 *
 * Set `prefix` to give cookie keys a prefix
 */
angular.module('app.services').service('Cookie', Cookie);

Cookie.$inject = ['$cookieStore'];
function Cookie ($cookieStore) {
    function CookieFactory (prefix) {
        return new Cookie(prefix);
    }

    function Cookie(prefix) {
        this.prefix = prefix;
    }

    /**
     * getCookieValue() tries to retrieve a value from the cookie, or returns default value
     *
     * @param field string: key to retrieve info from
     * @param defaultValue {*}: default value when nothing set on cache
     * @returns {*}: retrieved or default value
     */
    Cookie.prototype.get = function (field, defaultValue) {
        try {
            var value = $cookieStore.get(this.prefix + field);
            return (value !== undefined) ? value : defaultValue;
        } catch (error) {
            $cookieStore.remove(this.prefix + field);
            return defaultValue;
        }
    };

    /**
     * setCookieValue() sets value on the cookie
     *
     * It prefixes the field to make field unique for this controller
     *
     * @param field string: the key on which to store the value
     * @param value {*}: JSON serializable object to store
     */
    Cookie.prototype.put = function (field, value) {
        $cookieStore.put(this.prefix + field, value);
    };

    return CookieFactory;
}

})(angular);
(function(angular){
'use strict';
angular.module('app.services').service('HLDate', HLDate);

function HLDate () {
    /**
     * getSubtractedDate() subtracts x amount of days from the current date
     *
     * @param days (int): amount of days to subtract from the current date
     *
     * @returns (string): returns the subtracted date in a yyyy-mm-dd format
     */
    this.getSubtractedDate = function (days) {
        var date = new Date();
        date.setDate(date.getDate() - days);

        return date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate();
    };
}

})(angular);
(function(angular){
'use strict';
angular.module('app.services').service('HLFilters', HLFilters);

function HLFilters () {
    this.updateFilterQuery = function ($scope) {
        $scope.table.filterQuery = '';
        $scope.displayFilterClear = false;
        var filterStrings = [];

        for (var i = 0; i < $scope.filterList.length; i++) {
            var filter = $scope.filterList[i];
            if (filter.id && filter.id == 'archived') {
                if (!filter.selected) {
                    filterStrings.push('archived:false');
                }
                else {
                    $scope.displayFilterClear = true;
                }
            }
            else {
                if (filter.selected) {
                    filterStrings.push(filter.value);
                    $scope.displayFilterClear = true;
                }
            }
        }

        $scope.table.filterQuery = filterStrings.join(' AND ');
    };

    this.clearFilters = function ($scope) {
        for (var i = 0; i < $scope.filterList.length; i++) {
            $scope.filterList[i].selected = false;
        }

        $scope.updateFilterQuery();
    };
}

})(angular);
(function(angular){
'use strict';
angular.module('app.services').service('HLText', HLText);
function HLText () {
    /**
     * hlCapitalize() lowercases the whole string and makes the first character uppercase
     * This means 'STRING' becomes 'String'
     *
     * @returns (string): returns a string with only the first character uppercased
     */
    String.prototype.hlCapitalize = function () {
        var newString = this.toLowerCase();
        return newString.charAt(0).toUpperCase() + newString.substring(1);
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.services').factory('Notifications', Notifications);

Notifications.$inject = ['$resource'];

function Notifications ($resource) {
    return $resource('/api/utils/notifications/');
}

})(angular);
(function(angular){
'use strict';
angular.module('app.cases').controller('CaseAssignModal', CaseAssignModal);

CaseAssignModal.$inject = ['$modalInstance', 'myCase', 'Case', 'User'];
function CaseAssignModal ($modalInstance, myCase, Case, User) {
    var vm = this;
    vm.myCase = myCase;
    vm.currentAssigneeId = myCase.assigned_to_id;
    vm.users = [];

    vm.ok = ok;
    vm.cancel = cancel;

    activate();

    ////

    function activate() {
        _getUsers();
    }

    function _getUsers() {
        User.query({}, function(data) {
            vm.users = data;
        });
    }

    function ok () {
        // Update the assigned_to of the case and close the modal
        Case.update({id: vm.myCase.id, assigned_to: vm.currentAssigneeId}).$promise.then(function () {
            $modalInstance.close();
        });
    }

    function cancel () {
        $modalInstance.dismiss('cancel');
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig ($stateProvider) {
    $stateProvider.state('base.cases.create', {
        url: '/create',
        views: {
            '@': {
                templateUrl: '/cases/create',
                controller: CaseCreateController
            }
        },
        ncyBreadcrumb: {
            label: 'Create'
        }
    });
    $stateProvider.state('base.cases.create.fromContact', {
        url: '/contact/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: function(elem, attr) {
                    return '/cases/create/from_contact/' + elem.id +'/';
                },
                controller: CaseCreateController
            }
        },
        ncyBreadcrumb: {
            skip: true
        }
    });
    $stateProvider.state('base.cases.create.fromAccount', {
        url: '/account/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: function(elem, attr) {
                    return '/cases/create/from_account/' + elem.id +'/';
                },
                controller: CaseCreateController
            }
        },
        ncyBreadcrumb: {
            skip: true
        }
    });
}

angular.module('app.cases').controller('CaseCreateController', CaseCreateController);

CaseCreateController.$inject = ['$scope'];
function CaseCreateController ($scope) {
    $scope.conf.pageTitleBig = 'New case';
    $scope.conf.pageTitleSmall = 'making cases';
    HLCases.addAssignToMeButton();
    HLSelect2.init();
}

})(angular);
(function(angular){
'use strict';
angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig ($stateProvider) {
    $stateProvider.state('base.cases.detail.delete', {
        url: '/delete',
        views: {
            '@': {
                controller: CaseDeleteController
            }
        }
    });

}

angular.module('app.cases').controller('CaseDeleteController', CaseDeleteController);

CaseDeleteController.$inject = ['$http', '$state', '$stateParams'];
function CaseDeleteController ($http, $state, $stateParams) {
    var id = $stateParams.id;

    var req = {
        method: 'POST',
        url: '/cases/delete/' + id + '/',
        headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
    };

    $http(req).
        success(function(data, status, headers, config) {
            $state.go('base.cases');
        }).
        error(function(data, status, headers, config) {
            $state.go('base.cases');
        });
}

})(angular);
(function(angular){
'use strict';
angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig ($stateProvider) {
    $stateProvider.state('base.cases.detail', {
        url: '/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'cases/controllers/detail.html',
                controller: CaseDetailController,
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: '{{ case.subject }}'
        }
    });
}

angular.module('app.cases').controller('CaseDetailController', CaseDetailController);

CaseDetailController.$inject = ['$http', '$modal', '$scope', '$state', '$stateParams', 'CaseDetail', 'CaseStatuses'];
function CaseDetailController ($http, $modal, $scope, $state, $stateParams, CaseDetail, CaseStatuses) {
    var vm = this;
    $scope.conf.pageTitleBig = 'Case';
    $scope.conf.pageTitleSmall = 'the devil is in the details';
    var id = $stateParams.id;
    vm.case = CaseDetail.get({id: id});
    vm.caseStatuses = CaseStatuses.query();

    vm.getPriorityDisplay = getPriorityDisplay;
    vm.changeCaseStatus = changeCaseStatus;
    vm.assignCase = assignCase;
    vm.archive = archive;
    vm.unarchive = unarchive;
    vm.openPostponeWidget = openPostponeWidget;


    //////

    /**
     *
     * @returns {string}: A string which states what label should be displayed
     */
    function getPriorityDisplay () {
        if (vm.case.is_archived) {
            return 'label-default';
        } else {
            switch (vm.case.priority) {
                case 0:
                    return 'label-success';
                case 1:
                    return 'label-info';
                case 2:
                    return 'label-warning';
                case 3:
                    return 'label-danger';
                default :
                    return 'label-info';
            }
        }
    }

    function changeCaseStatus (status) {
        // TODO: LILY-XXX: Temporary call to change status of a case, will be replaced with an new API call later
        var req = {
            method: 'POST',
            url: '/cases/update/status/' + vm.case.id + '/',
            data: 'status=' + status,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        $http(req).
            success(function(data, status, headers, config) {
                vm.case.status = data.status;
            }).
            error(function(data, status, headers, config) {
                // Request failed proper error?
            });
    }

    function assignCase () {
        var assignee = '';

        if (vm.case.assigned_to_id != currentUser.id) {
            assignee = currentUser.id;
        }

        var req = {
            method: 'POST',
            url: '/cases/update/assigned_to/' + vm.case.id + '/',
            data: 'assignee=' + assignee,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        $http(req).
            success(function(data, status, headers, config) {
                if (data.assignee) {
                    vm.case.assigned_to_id = data.assignee.id;
                    vm.case.assigned_to_name = data.assignee.name;
                }
                else {
                    vm.case.assigned_to_id = null;
                    vm.case.assigned_to_name = null;
                }
            }).
            error(function(data, status, headers, config) {
                // Request failed propper error?
            });
    }

    /**
     * Archive a deal.
     * TODO: LILY-XXX: Change to API based archiving
     */
    function archive (id) {
        var req = {
            method: 'POST',
            url: '/cases/archive/',
            data: 'id=' + id,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        $http(req).
            success(function(data, status, headers, config) {
                vm.case.archived = true;
            }).
            error(function(data, status, headers, config) {
                // Request failed propper error?
            });
    }

    /**
     * Unarchive a deal.
     * TODO: LILY-XXX: Change to API based unarchiving
     */
    function unarchive (id) {
        var req = {
            method: 'POST',
            url: '/cases/unarchive/',
            data: 'id=' + id,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        $http(req).
            success(function(data, status, headers, config) {
                vm.case.archived = false;
            }).
            error(function(data, status, headers, config) {
                // Request failed propper error?
            });
    }

    function openPostponeWidget (myCase) {
        var modalInstance = $modal.open({
            templateUrl: 'cases/controllers/postpone.html',
            controller: 'CasePostponeModal',
            controllerAs: 'vm',
            size: 'sm',
            resolve: {
                myCase: function() {
                    return myCase
                }
            }
        });

        modalInstance.result.then(function() {
            $state.go($state.current, {}, {reload: true});
        });
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig ($stateProvider) {
    $stateProvider.state('base.cases.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: function (elem, attr) {
                    return '/cases/update/' + elem.id + '/';
                },
                controller: CaseEditController
            }
        },
        ncyBreadcrumb: {
            label: 'Edit'
        }
    });
}

angular.module('app.cases').controller('CaseEditController', CaseEditController);

CaseEditController.$inject = ['$scope', '$stateParams', 'CaseDetail'];
function CaseEditController ($scope, $stateParams, CaseDetail) {
    var id = $stateParams.id;
    var casePromise = CaseDetail.get({id: id}).$promise;

    casePromise.then(function(caseObject) {
        $scope.case = caseObject;
        $scope.conf.pageTitleBig = caseObject.subject;
        $scope.conf.pageTitleSmall = 'change is natural';
        HLSelect2.init();
    });
}

})(angular);
(function(angular){
'use strict';
angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig ($stateProvider) {
    $stateProvider.state('base.cases', {
        url: '/cases',
        views: {
            '@': {
                templateUrl: 'cases/controllers/list.html',
                controller: CaseListController
            }
        },
        ncyBreadcrumb: {
            label: 'Cases'
        }
    });
}

angular.module('app.cases').controller('CaseListController', CaseListController);

CaseListController.$inject = ['$http', '$location', '$modal', '$scope', '$state', 'Case', 'Cookie', 'HLDate', 'HLFilters'];
function CaseListController ($http, $location, $modal, $scope, $state, Case, Cookie, HLDate, HLFilters) {
    var cookie = Cookie('caseList');

    $scope.conf.pageTitleBig = 'Cases';
    $scope.conf.pageTitleSmall = 'do all your lookin\' here';

    // Setup search query
    var searchQuery = '';

    // Check if filter is set as query parameter
    var search = $location.search().search;
    if (search != undefined) {
        searchQuery = search;
    } else {
        // Get searchQuery from cookie
        searchQuery = cookie.get('searchQuery', '');
    }

    /**
     * table object: stores all the information to correctly display the table
     */
    $scope.table = {
        page: 1,  // current page of pagination: 1-index
        pageSize: 60,  // number of items per page
        totalItems: 0, // total number of items
        searchQuery: searchQuery,  // search query
        archived: cookie.get('archived', false),
        order: cookie.get('order', {
            ascending: true,
            column: 'expires'  // string: current sorted column
        }),
        visibility: cookie.get('visibility', {
            caseId: true,
            client: true,
            subject: true,
            priority: true,
            type: true,
            status: true,
            expires: true,
            assignedTo: true,
            createdBy: true,
            tags: true
        })
    };

    $scope.displayFilterClear = false;

    getFilterList();

    /**
     * Gets the filter list. Is either the value in the cookie or a new list
     *
     * @returns filterList (object): object containing the filter list
     */
    function getFilterList() {
        var filterListCookie = cookie.get('filterList', null);

        if (!filterListCookie) {
            var filterList = [
                {
                    name: 'Assigned to me',
                    value: 'assigned_to_id:' + $scope.currentUser.id,
                    selected: false
                },
                {
                    name: 'Assigned to nobody',
                    value: 'NOT(assigned_to_id:*)',
                    selected: false
                },
                {
                    name: 'Expired 7 days or more ago',
                    value: 'expires:[* TO ' + HLDate.getSubtractedDate(7) + ']',
                    selected: false
                },
                {
                    name: 'Expired 30 days or more ago',
                    value: 'expires:[* TO ' + HLDate.getSubtractedDate(30) + ']',
                    selected: false
                },
                {
                    name: 'Archived',
                    value: '',
                    selected: false,
                    id: 'archived'
                }
            ];

            // Update filterList for now
            $scope.filterList = filterList;

            Case.getCaseTypes().then(function (cases) {
                for (var key in cases) {
                    if (cases.hasOwnProperty(key)) {
                        filterList.push({
                            name: 'Case type ' + cases[key],
                            value: 'casetype_id:' + key,
                            selected: false
                        });
                    }
                }

                // Update filterList once AJAX call is done
                $scope.filterList = filterList;
                // Watch doesn't get triggered here, so manually call updateTableSettings
                updateTableSettings();
            });
        } else {
            // Cookie is set, so use it as the filterList
            $scope.filterList = filterListCookie;
        }
    }

    /**
     * updateTableSettings() sets scope variables to the cookie
     */
    function updateTableSettings() {
        cookie.put('searchQuery', $scope.table.searchQuery);
        cookie.put('archived', $scope.table.archived);
        cookie.put('order', $scope.table.order);
        cookie.put('visibility', $scope.table.visibility);
        cookie.put('filterList', $scope.filterList);
    }

    /**
     * updateCases() reloads the cases through a service
     *
     * Updates table.items and table.totalItems
     */
    function updateCases() {
        Case.getCases(
            $scope.table.searchQuery,
            $scope.table.page,
            $scope.table.pageSize,
            $scope.table.order.column,
            $scope.table.order.ascending,
            $scope.table.archived,
            $scope.table.filterQuery
        ).then(function (data) {
                $scope.table.items = data.cases;
                $scope.table.totalItems = data.total;
            }
        );
    }

    /**
     * Watches the model info from the table that, when changed,
     * needs a new set of cases
     */
    $scope.$watchGroup([
        'table.page',
        'table.order.column',
        'table.order.ascending',
        'table.searchQuery',
        'table.archived',
        'table.filterQuery'
    ], function () {
        updateTableSettings();
        updateCases();
    });

    /**
     * Watches the model info from the table that, when changed,
     * needs to store the info to the cache
     */
    $scope.$watchCollection('table.visibility', function () {
        updateTableSettings();
    });

    /**
     * Watches the filters so when the cookie is loaded,
     * the filterQuery changes and a new set of deals is fetched
     */
    $scope.$watchCollection('filterList', function () {
        $scope.updateFilterQuery();
    });

    /**
     * setSearchQuery() sets the search query of the table
     *
     * @param queryString string: string that will be set as the new search query on the table
     */
    $scope.setSearchQuery = function (queryString) {
        $scope.table.searchQuery = queryString;
    };

    $scope.toggleArchived = function () {
        $scope.table.archived = !$scope.table.archived;
    };

    $scope.updateFilterQuery = function () {
        HLFilters.updateFilterQuery($scope);
    };

    $scope.clearFilters = function () {
        HLFilters.clearFilters($scope);
    };

    /**
     * Deletes the case in django and updates the angular view
     */
    $scope.delete = function(id, subject, cases) {
        var req = {
            method: 'POST',
            url: '/cases/delete/' + id + '/',
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        if(confirm('Are you sure you want to delete case ' + subject + '?')){
            $http(req).
                success(function(data, status, headers, config) {
                    var index = $scope.table.items.indexOf(cases);
                    $scope.table.items.splice(index, 1);
                }).
                error(function(data, status, headers, config) {
                    // Request failed proper error?
                });
        }
    };

    $scope.assignTo = function(myCase) {
        var modalInstance = $modal.open({
            templateUrl: 'cases/controllers/assignto.html',
            controller: 'CaseAssignModal',
            controllerAs: 'vm',
            size: 'sm',
            resolve: {
                myCase: function() {
                    return myCase;
                }
            }
        });

        modalInstance.result.then(function() {
            $state.go($state.current, {}, {reload: true});
        });
    };
}

})(angular);
(function(angular){
'use strict';
angular.module('app.cases').controller('CasePostponeModal', CasePostponeModal);

CasePostponeModal.$inject = ['$filter', '$modalInstance', '$scope', 'Case', 'myCase'];
function CasePostponeModal ($filter, $modalInstance, $scope, Case, myCase) {
    var vm = this;
    vm.myCase = myCase;
    vm.pickerIsOpen = false;
    vm.expireDate = new Date(myCase.expires);
    vm.dateFormat = 'dd MMMM yyyy';
    vm.datepickerOptions = {
        startingDay: 1
    };

    vm.disabledDates = disabledDates;
    vm.openDatePicker = openDatePicker;
    vm.postponeWithDays = postponeWithDays;
    vm.getFutureDate = getFutureDate;

    activate();

    ////

    function activate() {
        _watchCloseDatePicker();
    }

    /**
     * When the datepicker popup is closed, update model and close modal
     *
     * @private
     */
    function _watchCloseDatePicker () {
        $scope.$watch('vm.pickerIsOpen', function(newValue, oldValue) {
            if (!newValue && oldValue) {
                _updateDayAndCloseModal();
            }
        });
    }

    function _updateDayAndCloseModal() {
        if (vm.expireDate != new Date(myCase.expires)) {
            // Update the expire date for this case
            var newDate = $filter('date')(vm.expireDate, 'yyyy-MM-dd');
            Case.update({id: myCase.id}, {expires: newDate}, function() {
                $modalInstance.close();
            })
        } else {
            $modalInstance.close();
        }
    }
    function disabledDates (date, mode) {
        return ( mode === 'day' && ( date.getDay() === 0 || date.getDay() === 6 ) );
    }

    function openDatePicker ($event) {
        $event.preventDefault();
        $event.stopPropagation();
        vm.pickerIsOpen = true;
    }

    function postponeWithDays (days) {
        vm.expireDate.setDate(vm.expireDate.getDate() + days);
        _updateDayAndCloseModal();
    }

    function getFutureDate(days) {
        var futureDate = new Date(vm.expireDate);
        return futureDate.setDate(futureDate.getDate() + days);
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.cases.directives').directive('caseListWidget', CaseListWidget);
function CaseListWidget(){
    return {
        restrict: 'E',
        replace: true,
        scope: {
            title: '@',
            list: '=',
            height: '=',
            addLink: '@'
        },
        templateUrl: 'cases/directives/list_widget.html'
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.cases.directives').directive('updateCaseExpireDate', updateCaseExpireDate);

function updateCaseExpireDate () {
    return {
        restrict: "A",
        link: function(scope, element, attrs) {

            var select = $('#id_priority');
            var daysToAdd = [5, 3, 1, 0];

            select.on('change', function(event) {
                var priority = parseInt(select.val());
                if(isNaN(select.val())){
                    priority = 3;
                }
                var due = addBusinessDays(new Date(), daysToAdd[priority]);
                var month = due.getMonth() + 1;
                if(month < 10){
                    month = '0' + month;
                }
                var expires = due.getDate() + '/' + month + '/' + due.getFullYear();
                $('#id_expires').val(expires);
                $('#id_expires_picker').datepicker('update', expires);
            });
        }
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.cases.services').factory('Case', Case);

Case.$inject = ['$http', '$resource', '$q', 'AccountDetail', 'ContactDetail'];
function Case ($http, $resource, $q, AccountDetail, ContactDetail) {

    var Case = $resource(
        '/api/cases/case/:id',
        {},
        {
            query: {
                url: '/search/search/?type=cases_case&filterquery=:filterquery',
                isArray: true,
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    var objects = [];
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function(obj) {
                            objects.push(obj);
                        });
                    }
                    return objects;
                }
            },
            update: {
                method: 'PATCH',
                params: {
                    id: '@id'
                }
            }
        }
    );

    Case.getCases = getCases;
    Case.getCaseTypes = getCaseTypes;
    Case.getMyCasesWidget = getMyCasesWidget;
    Case.getCallbackRequests = getCallbackRequests;
    Case.getUnassignedCasesForTeam = getUnassignedCasesForTeam;

    return Case;

    /////////

    /**
     * getCases() gets the cases from the search backend through a promise
     *
     * @param queryString string: current filter on the caselist
     * @param page int: current page of pagination
     * @param pageSize int: current page size of pagination
     * @param orderColumn string: current sorting of cases
     * @param orderedAsc {boolean}: current ordering
     * @param archived {boolean}: when true, only archived are fetched, if false, only active
     * @param filterQuery {string}: contains the filters which are used in ElasticSearch
     *
     * @returns Promise object: when promise is completed:
     *      {
     *          cases list: paginated cases objects
     *          total int: total number of case objects
     *      }
     */
    function getCases (queryString, page, pageSize, orderColumn, orderedAsc, archived, filterQuery) {

        return $http({
            url: '/search/search/',
            method: 'GET',
            params: {
                type: 'cases_case',
                q: queryString,
                page: page - 1,
                size: pageSize,
                sort: _getSorting(orderColumn, orderedAsc),
                filterquery: filterQuery
            }
        }).then(function(response) {
            return {
                cases: response.data.hits,
                total: response.data.total
            };
        });
    }

    function getCaseTypes () {
        return $http({
            url: '/cases/casetypes/',
            method: 'GET'
        }).then(function (response) {
            return response.data.casetypes;
        });
    }

    function _getSorting (field, sorting) {
        var sort = '';
        sort += sorting ? '-': '';
        sort += field;
        return sort;
    }

    /**
     * Service to return a resource for my cases widget
     */
    function getMyCasesWidget (field, sorting) {
        var deferred = $q.defer();
        var filterQuery = 'archived:false AND NOT casetype_name:Callback';
        filterQuery += ' AND assigned_to_id:' + currentUser.id;
        Case.query({
            filterquery: filterQuery,
            sort: _getSorting(field, sorting)
        }, function (cases) {
            deferred.resolve(cases);
        });

        return deferred.promise;
    }

    /**
     * Gets all cases with the 'callback' case type
     *
     * @returns cases with the callback case type
     */
    function getCallbackRequests (field, sorting) {
        var filterQuery = 'archived:false AND casetype_name:Callback';
        filterQuery += ' AND assigned_to_id:' + currentUser.id;

        var deferred = $q.defer();
        Case.query({
            filterquery: filterQuery,
            sort: _getSorting(field, sorting)
        }, function (cases) {
            angular.forEach(cases, function(callbackCase) {
                if (callbackCase.account) {
                    AccountDetail.get({id: callbackCase.account}, function(account) {
                        callbackCase.accountPhone = account.phone;
                    });
                }
                if (callbackCase.contact) {
                    ContactDetail.get({id: callbackCase.contact}, function(contact) {
                        callbackCase.contactPhone = contact.phone;
                    });
                }
            });
            deferred.resolve(cases);
        });
        return deferred.promise;
    }

    function getUnassignedCasesForTeam (teamId, field, sorting) {
        var filterQuery = 'archived:false AND _missing_:assigned_to_id';
        filterQuery += ' AND assigned_to_groups:' + teamId;

        return Case.query({
            filterquery: filterQuery,
            sort: _getSorting(field, sorting)
        }).$promise;
    }
}

})(angular);
(function(angular){
'use strict';
/**
 * $resource for Case model, now only used for detail page.
 */
angular.module('app.cases.services').factory('CaseDetail', CaseDetail);

CaseDetail.$inject = ['$resource'];
function CaseDetail ($resource) {
    return $resource(
        '/search/search/?type=cases_case&filterquery=id\::id',
        {},
        {
            get: {
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    if (data && data.hits && data.hits.length > 0) {
                        var obj = data.hits[0];
                        return obj;
                    }
                    return null;
                }
            },
            query: {
                url: '/search/search/?type=cases_case&filterquery=:filterquery',
                isArray: true,
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    var objects = [];
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function(obj) {
                            obj = $.extend(obj, {historyType: 'case', color: 'grey', date: obj.expires});
                            objects.push(obj);
                        });
                    }
                    return objects;
                }
            },
            totalize: {
                url: '/search/search/?type=cases_case&size=0&filterquery=:filterquery',
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    if (data && data.total) {
                        return {total: data.total};
                    }
                    return {total: 0};
                }
            }
        }
    );
}

})(angular);
(function(angular){
'use strict';
angular.module('app.cases.services').factory('CaseStatuses', CaseStatuses);

CaseStatuses.$inject = ['$resource'];
function CaseStatuses ($resource) {
    return $resource('/api/cases/statuses');
}

})(angular);
(function(angular){
'use strict';
angular.module('app.cases.services').factory('UnassignedTeamCases', UnassignedTeamCases);

UnassignedTeamCases.$inject = ['$resource'];
function UnassignedTeamCases ($resource) {
    return $resource('/api/cases/teams/:teamId/?is_assigned=False&is_archived=false&is_deleted=False')
}

})(angular);
(function(angular){
'use strict';
angular.module('app.contacts').config(contactsConfig);

contactsConfig.$inject = ['$stateProvider'];
function contactsConfig ($stateProvider) {
    $stateProvider.state('base.contacts.create', {
        url: '/create',
        views: {
            '@': {
                templateUrl: 'contacts/create/',
                controller: ContactCreateController
            }
        },
        ncyBreadcrumb: {
            label: 'Create'
        }
    });
    $stateProvider.state('base.contacts.create.fromAccount', {
        url: '/account/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: function(elem, attr){
                    return '/contacts/add/from_account/' + elem.id + '/';
                },
                controller: ContactCreateController
            }
        },
        ncyBreadcrumb:{
            skip: true
        }
    });
}

angular.module('app.contacts').controller('ContactCreateController', ContactCreateController);

ContactCreateController.$inject = ['$scope'];
function ContactCreateController ($scope) {
    $scope.conf.pageTitleBig = 'New contact';
    $scope.conf.pageTitleSmall = 'who did you talk to?';
}

})(angular);
(function(angular){
'use strict';
angular.module('app.contacts').config(contactsConfig);

contactsConfig.$inject = ['$stateProvider'];
function contactsConfig ($stateProvider) {
    $stateProvider.state('base.contacts.detail.delete', {
        url: '/delete',
        views: {
            '@': {
                controller: ContactDeleteController
            }
        }
    });
}

angular.module('app.contacts').controller('ContactDeleteController', ContactDeleteController);

ContactDeleteController.$inject = ['$state', '$stateParams', 'ContactTest'];
function ContactDeleteController($state, $stateParams, ContactTest) {
    var id = $stateParams.id;

    ContactTest.delete({
        id:id
    }, function() {  // On success
        $state.go('base.contacts');
    }, function(error) {  // On error
        // Error notification needed
        $state.go('base.contacts');
    });
}

})(angular);
(function(angular){
'use strict';
angular.module('app.contacts').config(contactsConfig);

contactsConfig.$inject = ['$stateProvider'];
function contactsConfig ($stateProvider) {
    $stateProvider.state('base.contacts.detail', {
        url: '/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'contacts/controllers/detail.html',
                controller: 'ContactDetailController'
            }
        },
        ncyBreadcrumb: {
            label: '{{ contact.name }}'
        },
        resolve: {
            contact: ['ContactDetail', '$stateParams', function (ContactDetail, $stateParams) {
                var contactId = $stateParams.id;
                return ContactDetail.get({id: contactId}).$promise
            }]
        }
    });
}

angular.module('app.contacts').controller('ContactDetailController', ContactDetail);

ContactDetail.$inject = ['$scope', '$stateParams', 'ContactDetail', 'CaseDetail', 'contact'];
function ContactDetail($scope, $stateParams, ContactDetail, CaseDetail, contact) {
    var id = $stateParams.id;

    $scope.contact = contact;

    if ($scope.contact.accounts) {
        $scope.contact.accounts.forEach(function(account) {
            var colleagueList = ContactDetail.query({filterquery: 'NOT(id:' + id + ') AND accounts.id:' + account.id});
            colleagueList.$promise.then(function(colleagues) {
                account.colleagueList = colleagues;
            })
        });
    }

    $scope.conf.pageTitleBig = 'Contact detail';
    $scope.conf.pageTitleSmall = 'the devil is in the details';

    $scope.caseList = CaseDetail.query({filterquery: 'contact:' + id});
    $scope.caseList.$promise.then(function(caseList) {
        $scope.caseList = caseList;
    });
}

})(angular);
(function(angular){
'use strict';
angular.module('app.contacts').config(contactsConfig);

contactsConfig.$inject = ['$stateProvider'];
function contactsConfig ($stateProvider) {
    $stateProvider.state('base.contacts.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: function(elem, attr) {
                    return '/contacts/edit/' + elem.id +'/';
                },
                controller: ContactEditController
            }
        },
        ncyBreadcrumb: {
            label: 'Edit'
        }
    });
}

angular.module('app.contacts').controller('ContactEditController', ContactEditController);

ContactEditController.$inject = ['$scope', '$stateParams', 'ContactDetail'];
function ContactEditController ($scope, $stateParams, ContactDetail) {
    var id = $stateParams.id;
    var contactPromise = ContactDetail.get({id: id}).$promise;

    contactPromise.then(function(contact) {
        $scope.contact = contact;
        $scope.conf.pageTitleBig = contact.name;
        $scope.conf.pageTitleSmall = 'change is natural';
        HLSelect2.init();
    });
}

})(angular);
(function(angular){
'use strict';
angular.module('app.contacts').config(contactsConfig);

contactsConfig.$inject = ['$stateProvider'];
function contactsConfig ($stateProvider) {
    $stateProvider.state('base.contacts', {
        url: '/contacts',
        views: {
            '@': {
                templateUrl: 'contacts/controllers/list.html',
                controller: ContactListController
            }
        },
        ncyBreadcrumb: {
            label: 'Contacts'
        }
    });
}

angular.module('app.contacts').controller('ContactListController', ContactListController);

ContactListController.$inject = ['$scope', '$window', 'Contact', 'Cookie', 'ContactTest'];
function ContactListController($scope, $window, Contact, Cookie, ContactTest) {
    var cookie = Cookie('contactList');

    $scope.conf.pageTitleBig = 'Contacts';
    $scope.conf.pageTitleSmall = 'do all your lookin\' here';

    /**
     * table object: stores all the information to correctly display the table
     */
    $scope.table = {
        page: 1,  // current page of pagination: 1-index
        pageSize: 20,  // number of items per page
        totalItems: 0, // total number of items
        filter: cookie.get('filter', ''),  // search filter
        order:  cookie.get('order', {
            ascending: true,
            column:  'modified'  // string: current sorted column
        }),
        visibility: cookie.get('visibility', {
            name: true,
            contactInformation: true,
            worksAt: true,
            created: true,
            modified: true,
            tags: true
        })};

    $scope.deleteContact = function(contact) {
        if (confirm('Are you sure?')) {
            ContactTest.delete({
                id:contact.id
            }, function() {  // On success
                var index = $scope.table.items.indexOf(contact);
                $scope.table.items.splice(index, 1);
            }, function(error) {  // On error
                alert('something went wrong.')
            })
        }
    };

    /**
     * updateTableSettings() sets scope variables to the cookie
     */
    function updateTableSettings() {
        cookie.put('filter', $scope.table.filter);
        cookie.put('order', $scope.table.order);
        cookie.put('visibility', $scope.table.visibility);
    }

    /**
     * updateContacts() reloads the contacts through a service
     *
     * Updates table.items and table.totalItems
     */
    function updateContacts() {
        Contact.query(
            $scope.table
        ).then(function(data) {
                $scope.table.items = data.contacts;
                $scope.table.totalItems = data.total;
            }
        );
    }

    /**
     * Watches the model info from the table that, when changed,
     * needs a new set of contacts
     */
    $scope.$watchGroup([
        'table.page',
        'table.order.column',
        'table.order.ascending',
        'table.filter'
    ], function() {
        updateTableSettings();
        updateContacts();
    });

    /**
     * Watches the model info from the table that, when changed,
     * needs to store the info to the cache
     */
    $scope.$watchCollection('table.visibility', function() {
        updateTableSettings();
    });

    /**
     * setFilter() sets the filter of the table
     *
     * @param queryString string: string that will be set as the new filter on the table
     */
    $scope.setFilter = function(queryString) {
        $scope.table.filter = queryString;
    };

    /**
     * exportToCsv() creates an export link and opens it
     */
    $scope.exportToCsv = function() {
        var getParams = '';

        // If there is a filter, add it
        if ($scope.table.filter) {
            getParams += '&export_filter=' + $scope.table.filter;
        }

        // Add all visible columns
        angular.forEach($scope.table.visibility, function(value, key) {
            if (value) {
                getParams += '&export_columns='+ key;
            }
        });

        // Setup url
        var url = '/contacts/export/';
        if (getParams) {
            url += '?' + getParams.substr(1);
        }

        // Open url
        $window.open(url);
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.contacts.directives').directive('contactDetailWidget', ContactDetailWidget);

function ContactDetailWidget() {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            contact: '=',
            height: '='
        },
        templateUrl: 'contacts/directives/detail_widget.html'
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.contacts.directives').directive('contactListWidget', ContactListWidget);

function ContactListWidget() {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            title: '@',
            list: '=',
            height: '=',
            accountId: '@',
            addLink: '@'
        },
        templateUrl: 'contacts/directives/list_widget.html'
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.contacts.services').factory('ContactDetail', ContactDetail);

ContactDetail.$inject = ['$resource'];
function ContactDetail ($resource) {
    function getPhone(contact) {
        if (contact.phone_mobile) return contact.phone_mobile[0];
        if (contact.phone_work) return contact.phone_work[0];
        if (contact.phone_other) return contact.phone_other[0];
        return '';
    }

    function getPhones(contact) {
        var phones = [];
        if (contact.phone_mobile) phones = phones.concat(contact.phone_mobile);
        if (contact.phone_work) phones = phones.concat(contact.phone_work);
        if (contact.phone_other) phones = phones.concat(contact.phone_other);
        return phones;
    }

    return $resource(
        '/search/search/?type=contacts_contact&filterquery=id\::id',
        {},
        {
            get: {
                transformResponse: function (data) {
                    data = angular.fromJson(data);
                    if (data && data.hits && data.hits.length > 0) {
                        var contact = data.hits[0];
                        contact.phones = getPhones(contact);
                        contact.phone = getPhone(contact);
                        return contact;
                    }
                    return null;
                }
            },
            query: {
                url: '/search/search/?type=contacts_contact&size=1000&filterquery=:filterquery',
                isArray: true,
                transformResponse: function (data) {
                    data = angular.fromJson(data);
                    var contacts = [];
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function (contact) {
                            contact.phones = getPhones(contact);
                            contact.phone = getPhone(contact);
                            contacts.push(contact);
                        });
                    }
                    return contacts;
                }
            }
        }
    )
}

})(angular);
(function(angular){
'use strict';
angular.module('app.contacts.services').factory('Contact', Contact);

Contact.$inject = ['$http'];
function Contact ($http) {
    var Contact = {};

    /**
     * getContacts() get the contacts from the search backend through a promise
     *
     * @param queryString string: current filter on the contactlist
     * @param page int: current page of pagination
     * @param pageSize int: current page size of pagination
     * @param orderColumn string: current sorting of contacts
     * @param orderedAsc {boolean}: current ordering
     *
     * @returns Promise object: when promise is completed:
     *      {
     *          contacts list: paginated contact objects
     *          total int: total number of contact objects
     *      }
     */
    var getContacts = function(queryString, page, pageSize, orderColumn, orderedAsc) {

        var sort = '';
        if (orderedAsc) sort += '-';
        sort += orderColumn;

        return $http({
            url: '/search/search/',
            method: 'GET',
            params: {
                type: 'contacts_contact',
                q: queryString,
                page: page - 1,
                size: pageSize,
                sort: sort
            }
        })
            .then(function(response) {
                return {
                    contacts: response.data.hits,
                    total: response.data.total
                };
            });
    };

    /**
     * query() makes it possible to query on contacts on backend search
     *
     * @param table object: holds all the info needed to get contacts from backend
     *
     * @returns Promise object: when promise is completed:
     *      {
     *          contacts list: paginated contact objects
     *          total int: total number of contact objects
     *      }
     */
    Contact.query = function(table) {
        return getContacts(table.filter, table.page, table.pageSize, table.order.column, table.order.ascending);
    };

    return Contact;
}


})(angular);
(function(angular){
'use strict';
angular.module('app.contacts.services').factory('ContactTest', ContactTest);

ContactTest.$inject = ['$resource'];
function ContactTest ($resource) {
    return $resource('/api/contacts/contact/:id/');
}

})(angular);
(function(angular){
'use strict';
angular.module('app.dashboard').config(dashboardConfig);

dashboardConfig.$inject = ['$stateProvider'];
function dashboardConfig ($stateProvider) {
    $stateProvider.state('base.dashboard', {
        url: '/',
        views: {
            '@': {
                templateUrl: 'dashboard/controllers/base.html',
                controller: DashboardController,
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: 'Dashboard'
        }
    });
}

angular.module('app.dashboard').controller('DashboardController', DashboardController);

DashboardController.$inject = ['$scope'];
function DashboardController ($scope) {
    $scope.conf.pageTitleBig = 'Dashboard';
    $scope.conf.pageTitleSmall = 'statistics and usage';
}

})(angular);
(function(angular){
'use strict';
angular.module('app.dashboard.directives').directive('callbackRequests', CallbackRequestsDirective);

function CallbackRequestsDirective () {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/callback.html',
        controller: CallbackRequestsController,
        controllerAs: 'vm'
    }
}

CallbackRequestsController.$inject = ['$scope', 'Case', 'Cookie'];
function CallbackRequestsController ($scope, Case, Cookie) {
    var vm = this;
    var cookie = Cookie('callbackWidget');

    vm.table = {
        order: cookie.get('order', {
            ascending: true,
            column: 'created'  // string: current sorted column
        }),
        items: []
    };

    activate();

    ///////////

    function activate () {
        _watchTable();
    }

    function _getCallbackRequests () {
        Case.getCallbackRequests(
            vm.table.order.column,
            vm.table.order.ascending
        ).then(function (callbackRequests) {
            vm.table.items = callbackRequests;
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.ascending', 'vm.table.order.column'], function() {
            _getCallbackRequests();
            cookie.put('order', vm.table.order);
        })
    }
}

})(angular);
(function(angular){
'use strict';

angular.module('app.dashboard.directives').directive('dealsToCheck', dealsToCheckDirective);

function dealsToCheckDirective () {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/dealstocheck.html',
        controller: DealsToCheckController,
        controllerAs: 'vm'
    }
}

DealsToCheckController.$inject = ['$scope', 'Cookie', 'Deal', 'UserTeams'];
function DealsToCheckController ($scope, Cookie, Deal, UserTeams) {
    var cookie = Cookie('dealsToCheckkWidget');
    var vm = this;
    vm.users = [];
    vm.table = {
        order: cookie.get('order', {
            ascending: true,
            column: 'closing_date'  // string: current sorted column
        }),
        items: [],
        selectedUserId: cookie.get('selectedUserId')
    };
    vm.markDealAsChecked = markDealAsChecked;
    activate();

    ///////////

    function activate () {
        _watchTable();
        _getUsers();
    }

    function _getDealsToCheck () {
        if (vm.table.selectedUserId) {
            Deal.getDealsToCheck(
                vm.table.order.column,
                vm.table.order.ascending,
                vm.table.selectedUserId
            ).then(function (deals) {
                vm.table.items = deals;
            });
        }
    }

    function _getUsers() {
        UserTeams.mine(function (teams) {
            angular.forEach(teams, function (team) {
                vm.users = vm.users.concat(team.user_set);
            });
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.ascending', 'vm.table.order.column', 'vm.table.selectedUserId'], function() {
            _getDealsToCheck();
            cookie.put('order', vm.table.order);
            cookie.put('selectedUserId', vm.table.selectedUserId);
        })
    }

    function markDealAsChecked (deal) {
        deal.markDealAsChecked().then(function() {
           vm.table.items.splice(vm.table.items.indexOf(deal), 1);
        });
    }

}

})(angular);
(function(angular){
'use strict';

angular.module('app.dashboard.directives').directive('feedback', feedbackDirective);

function feedbackDirective () {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/feedback.html',
        controller: FeedbackController,
        controllerAs: 'vm'
    }
}

FeedbackController.$inject = ['$scope', '$state', 'Account', 'Cookie', 'Deal'];
function FeedbackController ($scope, $state, Account, Cookie, Deal) {
    var cookie = Cookie('feedbackWidget');

    var vm = this;
    vm.table = {
        order: cookie.get('order', {
            ascending: true,
            column: 'closing_date'  // string: current sorted column
        }),
        items: []
    };

    vm.feedbackFormSentForDeal = feedbackFormSentForDeal;
    vm.openFeedbackForm = openFeedbackForm;

    activate();

    ///////////

    function activate () {
        _watchTable();
    }

    function _getFeedbackDeals () {
        Deal.getFeedbackDeals(
            vm.table.order.column,
            vm.table.order.ascending
        ).then(function (deals) {
            vm.table.items = deals;
        });
    }

    function feedbackFormSentForDeal (deal) {
        deal.feedbackFormSent().then(function() {
           vm.table.items.splice(vm.table.items.indexOf(deal), 1);
        });
    }

    function openFeedbackForm (deal) {
        Account.get({id: deal.account}, function(account) {
            var emailAddress = account.getEmailAddress();
            if (emailAddress) {
                $state.go('base.email.composeEmail', {email: emailAddress.email_address});
            } else {
                $state.go('base.email.compose');
            }
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.ascending', 'vm.table.order.column'], function() {
            _getFeedbackDeals();
            cookie.put('order', vm.table.order);
        })
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.dashboard.directives').directive('followUp', followUpDirective);

function followUpDirective (){
    return {
        scope: {},
        templateUrl: 'dashboard/directives/followup.html',
        controller: FollowUpController,
        controllerAs: 'vm'
    }
}

FollowUpController.$inject = ['$modal', '$scope', 'Deal', 'Cookie'];
function FollowUpController ($modal, $scope, Deal, Cookie){

    var cookie = Cookie('followupWidget');

    var vm = this;
    vm.table = {
        order: cookie.get('order', {
            ascending: true,
            column: 'created'
        }),
        items: []
    };

    vm.openFollowUpWidgetModal = openFollowUpWidgetModal;

    activate();

    //////

    function activate(){
        _watchTable();
    }

    function _getFollowUp(){
        Deal.getFollowUpWidgetData(
            vm.table.order.column,
            vm.table.order.ascending
        ).then(function (data){
            vm.table.items = data;
        });
    }

    function openFollowUpWidgetModal(followUp){
        var modalInstance = $modal.open({
            templateUrl: 'deals/controllers/followup_widget.html',
            controller: 'FollowUpWidgetModal',
            controllerAs: 'vm',
            size: 'md',
            resolve: {
                followUp: function(){
                    return followUp;
                }
            }
        });

        modalInstance.result.then(function() {
            _getFollowUp();
        });
    }

    function _watchTable(){
        $scope.$watchGroup(['vm.table.order.ascending', 'vm.table.order.column'], function() {
            _getFollowUp();
            cookie.put('order', vm.table.order);
        })
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.dashboard.directives').directive('myCases', myCasesDirective);

function myCasesDirective () {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/mycases.html',
        controller: MyCasesController,
        controllerAs: 'vm'
    }
}

MyCasesController.$inject = ['$modal', '$scope', 'Case', 'Cookie'];
function MyCasesController ($modal, $scope, Case, Cookie) {
    var cookie = Cookie('myCasesWidget');

    var vm = this;
    vm.table = {
        order: cookie.get('order', {
            ascending: true,
            column: 'expires'  // string: current sorted column
        }),
        items: []
    };

    vm.openPostponeWidget = openPostponeWidget;

    activate();

    /////

    function activate() {
        _watchTable();
    }

    function _getMyCases() {
        Case.getMyCasesWidget(
            vm.table.order.column,
            vm.table.order.ascending
        ).then(function (data) {
            vm.table.items = data;
        });
    }

    function openPostponeWidget(myCase) {
        var modalInstance = $modal.open({
            templateUrl: 'cases/controllers/postpone.html',
            controller: 'CasePostponeModal',
            controllerAs: 'vm',
            size: 'sm',
            resolve: {
                myCase: function() {
                    return myCase
                }
            }
        });

        modalInstance.result.then(function() {
            _getMyCases();
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.ascending', 'vm.table.order.column'], function() {
            _getMyCases();
            cookie.put('order', vm.table.order);
        })
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.dashboard.directives').directive('queueSize', queueSizeDirective);

function queueSizeDirective (){
    return {
        scope: {},
        templateUrl: 'dashboard/directives/queuesize.html',
        controller: QueueSizeController
    }
}

QueueSizeController.$inject = ['$filter', '$http', '$interval', '$scope'];
function QueueSizeController ($filter, $http, $interval, $scope) {
    $scope.show = false;
    $scope.currentUser = currentUser;
    if (!currentUser.isSuperUser) return;
    $scope.labels = [];
    $scope.series = ['Queue Size'];
    $scope.data = [[]];
    $scope.options = {
        animation: false
    };
    $scope.queueName = 'queue1';

    var getQueueInfo = function() {
        $http.get('/api/utils/queues/' + $scope.queueName + '/').then(function(data){
            $scope.labels.push($filter('date')(Date.now(), 'H:mm:ss'));
            $scope.data[0].push(data.data.size);
            if ($scope.data[0].length > 15) {
                $scope.data[0].shift();
                $scope.labels.shift();
            }
            $scope.totalSize = data.data.total_messages;
            $scope.show = true;
        }, function() {
            $interval.cancel(stop);
            $scope.show = false;
        });
    };
    //Fetch again every 10 seconds
    getQueueInfo();
    var stop = $interval(getQueueInfo, 10000);

    $scope.$on('$destroy', function() {
        // Make sure that the interval is destroyed too
        if (angular.isDefined(stop)) {
            $interval.cancel(stop);
            stop = undefined;
        }
    });
}

})(angular);
(function(angular){
'use strict';
angular.module('app.dashboard.directives').directive('teams', teamsDirective);

function teamsDirective () {
    return {
        templateUrl: 'dashboard/directives/teams.html',
        controller: TeamsController,
        controllerAs: 'vm'
    }
}

TeamsController.$inject = ['UserTeams'];
function TeamsController (UserTeams) {
    var vm = this;
    vm.teams = [];

    activate();

    /////

    function activate() {
        _getTeams();
    }

    function _getTeams() {
        UserTeams.mine(function(teams) {
            vm.teams = teams;
        });
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.dashboard.directives').directive('unassignedCases', unassignedCasesDirective);

function unassignedCasesDirective () {
    return {
        templateUrl: 'dashboard/directives/unassignedcases.html',
        controller: UnassignedCasesController,
        controllerAs: 'vm',
        bindToController: true,
        scope: {
            team: '='
        }
    }
}

UnassignedCasesController.$inject = ['$http', '$scope', 'Case', 'Cookie'];
function UnassignedCasesController ($http, $scope, Case, Cookie) {
    var vm = this;
    var cookie = Cookie('unassignedCasesForTeam' + vm.team.id + 'Widget');

    vm.table = {
        order: cookie.get('order', {
            ascending: true,
            column: 'id'  // string: current sorted column
        }),
        items: []
    };

    vm.assignToMe = assignToMe;

    activate();

    /////

    function activate() {
        _watchTable();
    }

    function _getUnassignedCases() {
        Case.getUnassignedCasesForTeam(
            vm.team.id,
            vm.table.order.column,
            vm.table.order.ascending
        ).then(function(cases) {
            vm.table.items = cases;
        });
    }

    function assignToMe (caseObj){
        if(confirm('Assign this case to yourself?')){
            var req = {
                method: 'POST',
                url: '/cases/update/assigned_to/' + caseObj.id + '/',
                data: 'assignee=' + currentUser.id,
                headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
            };

            $http(req).success(function() {
                vm.table.items.splice(vm.table.items.indexOf(caseObj), 1);
                $scope.loadNotifications();
            });
        }
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.ascending', 'vm.table.order.column'], function() {
             _getUnassignedCases();
            cookie.put('order', vm.table.order);
        })
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.dashboard.directives').directive('unreadEmail', unreadEmailDirective);

function unreadEmailDirective () {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/unreademail.html',
        controller: UnreadEmailController,
        controllerAs: 'vm'
    }
}

UnreadEmailController.$inject = ['$scope', 'EmailMessage', 'Cookie'];
function UnreadEmailController ($scope, EmailMessage, Cookie) {
    var cookie = Cookie('unreadEmailWidget');

    var vm = this;
    vm.table = {
        order: cookie.get('order', {
            ascending: true,
            column: 'sent_date'  // string: current sorted column
        }),
        items: []
    };
    activate();

    //////

    function activate() {
        _watchTable();
    }

    function _getMessages () {
        EmailMessage.getDashboardMessages(
            vm.table.order.column,
            vm.table.order.ascending
        ).then(function (messages) {
            vm.table.items = messages;
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.ascending', 'vm.table.order.column'], function() {
            _getMessages();
            cookie.put('order', vm.table.order);
        })
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.deals').config(dealsConfig);

dealsConfig.$inject = ['$stateProvider'];
function dealsConfig ($stateProvider) {
    $stateProvider.state('base.deals.create', {
        url: '/create',
        views: {
            '@': {
                templateUrl: '/deals/create',
                controller: DealCreateController
            }
        },
        ncyBreadcrumb: {
            label: 'New'
        }
    });
    $stateProvider.state('base.deals.create.fromAccount', {
        url: '/account/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: function(elem, attr) {
                    return '/deals/create/from_account/' + elem.id +'/';
                },
                controller: DealCreateController
            }
        },
        ncyBreadcrumb: {
            skip: true
        }
    });
}

angular.module('app.deals').controller('DealCreateController', DealCreateController);

DealCreateController.$inject = ['$scope'];
function DealCreateController ($scope) {
    $scope.conf.pageTitleBig = 'New deal';
    $scope.conf.pageTitleSmall = 'making deals';
}

})(angular);
(function(angular){
'use strict';
angular.module('app.deals').config(dealsConfig);

dealsConfig.$inject = ['$stateProvider'];
function dealsConfig ($stateProvider) {
    $stateProvider.state('base.deals.detail.delete', {
        url: '/delete',
        views: {
            '@': {
                controller: DealDeleteController
            }
        }
    });
}

angular.module('app.deals').controller('DealDeleteController', DealDeleteController);

DealDeleteController.$inject = ['$http', '$state', '$stateParams'];
function DealDeleteController ($http, $state, $stateParams) {
    var id = $stateParams.id;
    var req = {
        method: 'POST',
        url: '/deals/delete/' + id + '/',
        headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
    };

    $http(req).
        success(function(data, status, headers, config) {
            $state.go('base.deals');
        }).
        error(function(data, status, headers, config) {
            $state.go('base.deals');
        });
}

})(angular);
(function(angular){
'use strict';
angular.module('app.deals').config(dealsConfig);

dealsConfig.$inject = ['$stateProvider'];
function dealsConfig ($stateProvider) {
    $stateProvider.state('base.deals.detail', {
        url: '/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'deals/controllers/detail.html',
                controller: DealDetailController
            }
        },
        ncyBreadcrumb: {
            label: '{{ deal.name }}'
        }
    });
}

angular.module('app.deals').controller('DealDetailController', DealDetailController);

DealDetailController.$inject = ['$http', '$scope', '$stateParams', 'DealDetail', 'DealStages'];
function DealDetailController ($http, $scope, $stateParams, DealDetail, DealStages) {
    $scope.conf.pageTitleBig = 'Deal detail';
    $scope.conf.pageTitleSmall = 'the devil is in the details';

    var id = $stateParams.id;

    $scope.deal = DealDetail.get({id: id});
    $scope.dealStages = DealStages.query();

    /**
     * Change the state of a deal
     */
    $scope.changeState = function(stage) {
        var newStage = stage;

        var req = {
            method: 'POST',
            url: '/deals/update/stage/' + $scope.deal.id + '/',
            data: 'stage=' + stage,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        $http(req).
            success(function(data, status, headers, config) {
                $scope.deal.stage = newStage;
                $scope.deal.stage_name = data.stage;
                if(data.closed_date !== undefined){
                    $scope.deal.closing_date = data.closed_date;
                }
                $scope.loadNotifications();
            }).
            error(function(data, status, headers, config) {
                // Request failed propper error?
            });
    };

    /**
     * Archive a deal
     */
    $scope.archive = function(id) {
        var req = {
            method: 'POST',
            url: '/deals/archive/',
            data: 'id=' + id,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        $http(req).
            success(function(data, status, headers, config) {
                $scope.deal.archived = true;
            }).
            error(function(data, status, headers, config) {
                // Request failed propper error?
            });
    };

    /**
     * Unarchive a deal
     */
    $scope.unarchive = function(id) {
        var req = {
            method: 'POST',
            url: '/deals/unarchive/',
            data: 'id=' + id,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        $http(req).
            success(function(data, status, headers, config) {
                $scope.deal.archived = false;
            }).
            error(function(data, status, headers, config) {
                // Request failed propper error?
            });
    };
}

})(angular);
(function(angular){
'use strict';
angular.module('app.deals').config(dealsConfig);

dealsConfig.$inject = ['$stateProvider'];
function dealsConfig ($stateProvider) {
    $stateProvider.state('base.deals.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: function (elem, attr) {
                    return '/deals/update/' + elem.id + '/';
                },
                controller: DealEditController
            }
        },
        ncyBreadcrumb: {
            label: 'Edit'
        }
    });
}

angular.module('app.deals').controller('DealEditController', DealEditController);

DealEditController.$inject = ['$scope', '$stateParams', 'DealDetail'];
function DealEditController ($scope, $stateParams, DealDetail) {
    var id = $stateParams.id;
    var dealPromise = DealDetail.get({id: id}).$promise;

    dealPromise.then(function(deal) {
        $scope.deal = deal;
        $scope.conf.pageTitleBig = 'Edit ' + deal.name;
        $scope.conf.pageTitleSmall = 'change is natural';
    })
}

})(angular);
(function(angular){
'use strict';
angular.module('app.deals').controller('FollowUpWidgetModal', FollowUpWidgetModalController);

FollowUpWidgetModalController.$inject = ['$filter', '$modalInstance', 'Deal', 'DealStages', 'followUp'];
function FollowUpWidgetModalController ($filter, $modalInstance, Deal, DealStages, followUp) {
    var vm = this;
    vm.dealStages = [];
    vm.selectedStage = { id: followUp.stage, name: followUp.stage_name };
    vm.followUp = followUp;
    vm.pickerIsOpen = false;
    vm.closingDate = new Date(followUp.closing_date);
    vm.dateFormat = 'dd MMMM yyyy';
    vm.datepickerOptions = {
        startingDay: 1
    };

    vm.openDatePicker = openDatePicker;
    vm.saveModal = saveModal;
    vm.closeModal = closeModal;

    activate();

    function activate(){
        _getDealStages();
    }

    function _getDealStages(){
        DealStages.query({}, function(data){
            vm.dealStages = [];
            for(var i = 0; i < data.length; i++){
                vm.dealStages.push({ id: data[i][0], name: data[i][1]});
            }
        });
    }

    function saveModal(){
        var newDate = $filter('date')(vm.closingDate, 'yyyy-MM-dd');
        var newStage = vm.selectedStage.id;
        Deal.update({id: followUp.id}, {stage: newStage, expected_closing_date: newDate}, function() {
            $modalInstance.close();
        });
    }

    function openDatePicker($event){
        $event.preventDefault();
        $event.stopPropagation();
        vm.pickerIsOpen = true;
    }

    function closeModal(){
        $modalInstance.close();
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.deals').config(dealsConfig);

dealsConfig.$inject = ['$stateProvider'];
function dealsConfig ($stateProvider) {
    $stateProvider.state('base.deals', {
        url: '/deals',
        views: {
            '@': {
                templateUrl: 'deals/controllers/list.html',
                controller: DealListController
            }
        },
        ncyBreadcrumb: {
            label: 'Deals'
        }
    });
}

angular.module('app.deals').controller('DealListController', DealListController);

DealListController.$inject = ['$http', '$location', '$scope', 'Cookie', 'Deal', 'HLDate', 'HLFilters'];
function DealListController($http, $location, $scope, Cookie, Deal, HLDate, HLFilters) {
    var cookie = Cookie('dealList');

    $scope.conf.pageTitleBig = 'Deals';
    $scope.conf.pageTitleSmall = 'do all your lookin\' here';

    // Setup search query
    var searchQuery = '';

    // Check if searchQuery is set as query parameter
    var search = $location.search().search;
    if (search != undefined) {
        searchQuery = search;
    } else {
        // Get searchQuery from cookie
        searchQuery = cookie.get('searchQuery', '');
    }

    /**
     * table object: stores all the information to correctly display the table
     */
    $scope.table = {
        page: 1,  // current page of pagination: 1-index
        pageSize: 20,  // number of items per page
        totalItems: 0, // total number of items
        searchQuery: searchQuery,  // search query
        filterQuery: '',
        archived: cookie.get('archived', false),
        order:  cookie.get('order', {
            ascending: true,
            column:  'closing_date'  // string: current sorted column
        }),
        visibility: cookie.get('visibility', {
            deal: true,
            stage: true,
            created: true,
            name: true,
            amountOnce: true,
            amountRecurring: true,
            assignedTo: true,
            closingDate: true,
            feedbackFormSent: true,
            newBusiness: true,
            tags: true
        })};

    /**
     * stores the selected filters
     */
    $scope.filterList = cookie.get('filterList', [
        {
            name: 'Assigned to me',
            value: 'assigned_to_id:' + currentUser.id,
            selected: false
        },
        {
            name: 'New business',
            value: 'new_business:true',
            selected: false
        },
        {
            name: 'Proposal stage',
            value: 'stage:1',
            selected: false
        },
        {
            name: 'Won stage',
            value: 'stage:2',
            selected: false
        },
        {
            name: 'Called',
            value: 'stage:4',
            selected: false
        },
        {
            name: 'Emailed',
            value: 'stage:5',
            selected: false
        },
        {
            name: 'Feedback form not sent',
            value: 'feedback_form_sent:false',
            selected: false
        },
        {
            name: 'Age between 7 and 30 days',
            value: 'created:[' + HLDate.getSubtractedDate(30) + ' TO ' + HLDate.getSubtractedDate(7) + ']',
            selected: false
        },
        {
            name: 'Age between 30 and 120 days',
            value: 'created:[' + HLDate.getSubtractedDate(120) + ' TO ' + HLDate.getSubtractedDate(30) + ']',
            selected: false
        },
        {
            name: 'Archived',
            value: '',
            selected: false,
            id: 'archived'
        }
    ]);

    /**
     * updateTableSettings() sets scope variables to the cookie
     */
    function updateTableSettings() {
        cookie.put('searchQuery', $scope.table.searchQuery);
        cookie.put('archived', $scope.table.archived);
        cookie.put('order', $scope.table.order);
        cookie.put('visibility', $scope.table.visibility);
        cookie.put('filterList', $scope.filterList);
    }

    /**
     * updateDeals() reloads the deals through a service
     *
     * Updates table.items and table.totalItems
     */
    function updateDeals() {
        Deal.getDeals(
            $scope.table.searchQuery,
            $scope.table.page,
            $scope.table.pageSize,
            $scope.table.order.column,
            $scope.table.order.ascending,
            $scope.table.filterQuery
        ).then(function(deals) {
            $scope.table.items = deals;
            $scope.table.totalItems = deals.length ? deals[0].total_size: 0;
        });
    }

    /**
     * Watches the model info from the table that, when changed,
     * needs a new set of deals
     */
    $scope.$watchGroup([
        'table.page',
        'table.order.column',
        'table.order.ascending',
        'table.searchQuery',
        'table.archived',
        'table.filterQuery'
    ], function() {
        updateTableSettings();
        updateDeals();
    });

    /**
     * Watches the model info from the table that, when changed,
     * needs to store the info to the cache
     */
    $scope.$watchCollection('table.visibility', function() {
        updateTableSettings();
    });

    /**
     * Watches the filters so when the cookie is loaded,
     * the filterQuery changes and a new set of deals is fetched
     */
    $scope.$watchCollection('filterList', function() {
        $scope.updateFilterQuery();
    });

    /**
     * setSearchQuery() sets the search query of the table
     *
     * @param queryString string: string that will be set as the new search query on the table
     */
    $scope.setSearchQuery = function(queryString) {
        $scope.table.searchQuery = queryString;
    };

    $scope.toggleArchived = function() {
        $scope.table.archived = !$scope.table.archived;
    };

    $scope.updateFilterQuery = function() {
        HLFilters.updateFilterQuery($scope);
    };

    $scope.clearFilters = function() {
        HLFilters.clearFilters($scope);
    };

    /**
     * Deletes the deal in django and updates the angular view
     */
    $scope.delete = function(id, name, deal) {
        var req = {
            method: 'POST',
            url: '/deals/delete/' + id + '/',
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        if(confirm("Are you sure you want to delete deal " + name + "?")){
            $http(req).
                success(function(data, status, headers, config) {
                    var index = $scope.table.items.indexOf(deal);
                    $scope.table.items.splice(index, 1);
                }).
                error(function(data, status, headers, config) {
                    // Request failed propper error?
                });
        }
    };
}

})(angular);
(function(angular){
'use strict';
angular.module('app.deals.directives').directive('dealListWidget', DealListWidgetDirective);

function DealListWidgetDirective () {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            title: '@',
            list: '=',
            height: '=',
            addLink: '@'
        },
        templateUrl: 'deals/directives/list_widget.html'
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.deals.services').factory('Deal', Deal);

Deal.$inject = ['$resource'];
function Deal ($resource) {
    var Deal = $resource(
        '/api/deals/deal/:id',
        null,
        {
            update: {
                method: 'PUT',
                params: {
                    id: '@id'
                }
            },
            query: {
                url: '/search/search/',
                method: 'GET',
                params:
                {
                    type: 'deals_deal'
                },
                isArray: true,
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    var objects = [];
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function(obj) {
                            obj = $.extend(obj, {
                                historyType: 'deal',
                                color: 'blue',
                                date: obj.modified,
                                total_size: data.total
                            });
                            objects.push(obj)
                        });
                    }
                    return objects;
                }
            }
        }
    );

    Deal.getDeals = getDeals;
    Deal.getDealsToCheck = getDealsToCheck;
    Deal.getFeedbackDeals = getFeedbackDeals;
    Deal.getFollowUpWidgetData = getFollowUpWidgetData;
    Deal.prototype.markDealAsChecked = markDealAsChecked;
    Deal.prototype.feedbackFormSent = feedbackFormSent;

    /////

    /**
     * getDeals() gets the deals from the search backend through a promise
     *
     * @param queryString string: current search query on the deallist
     * @param page int: current page of pagination
     * @param pageSize int: current page size of pagination
     * @param orderColumn string: current sorting of deals
     * @param orderedAsc {boolean}: current ordering
     * @param filterQuery {string}: contains the filters which are used in ElasticSearch
     *
     * @returns Promise object: when promise is completed:
     *      {
     *          deals list: paginated deals objects
     *          total int: total number of deal objects
     *      }
     */
    function getDeals (queryString, page, pageSize, orderColumn, orderedAsc, filterQuery) {
        var sort = '';
        if (orderedAsc) sort += '-';
        sort += orderColumn;

        return Deal.query({
            q: queryString,
            page: page - 1,
            size: pageSize,
            sort: sort,
            filterquery: filterQuery
        }, function (deals) {
            if (deals.length) {
                return {
                    deals: deals,
                    total: deals[0].total_size
                };
            }
        }).$promise;
    }

    function getDealsToCheck (column, ordering, userId) {

        var filterQuery = 'stage:2 AND is_checked:false';
        if (userId) {
            filterQuery += ' AND assigned_to_id:' + userId;
        }
        return getDeals('', 1, 20, column, ordering, filterQuery);
    }

    function getFeedbackDeals (column, ordering) {
        var filterQuery = 'stage:2 AND feedback_form_sent:false AND assigned_to_id:' + currentUser.id;
        return getDeals('', 1, 20, column, ordering, filterQuery);
    }

    function getFollowUpWidgetData (column, ordering){
        var filterQuery = '(stage: 0 OR stage: 1 OR stage: 4 OR stage: 5) AND assigned_to_id: ' + currentUser.id;
        return getDeals('', 1, 20, column, ordering, filterQuery);
    }

    function feedbackFormSent () {
        var deal = this;
        deal.feedback_form_sent = true;
        return deal.$update();
    }

    function markDealAsChecked () {
        var deal = this;
        deal.is_checked = true;
        return deal.$update();
    }

    return Deal;
}

})(angular);
(function(angular){
'use strict';
angular.module('app.deals.services').factory('DealDetail', DealDetail);

DealDetail.$inject = ['$resource'];
function DealDetail ($resource) {
    return $resource(
        '/search/search/?type=deals_deal&filterquery=id\::id',
        {},
        {
            get: {
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    if (data && data.hits && data.hits.length > 0) {
                        var obj = data.hits[0];
                        return obj;
                    }
                    return null;
                }
            },
            query: {
                url: '/search/search/?type=deals_deal&filterquery=:filterquery',
                isArray: true,
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    var objects = [];
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function(obj) {
                            obj = $.extend(obj, {historyType: 'deal', color: 'blue', date: obj.modified});
                            objects.push(obj)
                        });
                    }
                    return objects;
                }
            },
            totalize: {
                url: '/search/search/?type=deals_deal&size=0&filterquery=:filterquery',
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    if (data && data.total) {
                        return {total: data.total};
                    }
                    return {total: 0};
                }
            }
        }
    );
}

})(angular);
(function(angular){
'use strict';
angular.module('app.deals.services').factory('DealStages', DealStages);

DealStages.$inject = ['$resource'];

function DealStages ($resource) {
    return $resource('/api/deals/stages');
}

})(angular);
(function(angular){
'use strict';
angular.module('app.email').config(emailConfig);
emailConfig.$inject = ['$stateProvider', '$urlRouterProvider'];
function emailConfig($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.when('/email', '/email/all/INBOX');
    $stateProvider.state('base.email', {
        url: '/email',
        views: {
            '@': {
                templateUrl: 'email/controllers/base.html',
                controller: EmailBaseController,
                controllerAs: 'vm'
            },
            'labelList@base.email': {
                templateUrl: 'email/controllers/label_list.html',
                controller: 'LabelListController',
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: 'Email'
        },
        resolve: {
            primaryEmailAccountId: ['$q', 'User', function($q, User) {
                var deferred = $q.defer();
                User.me(null, function(data) {
                    deferred.resolve(data.primary_email_account);
                });
                return deferred.promise;
            }]
        }
    });
}

angular.module('app.email').controller('EmailBaseController', EmailBaseController);

EmailBaseController.$inject = ['$scope'];
function EmailBaseController ($scope) {
    $scope.conf.pageTitleBig = 'Email';
    $scope.conf.pageTitleSmall = 'sending love through the world!';
}

})(angular);
(function(angular){
'use strict';
angular.module('app.email').config(emailConfig);
emailConfig.$inject = ['$stateProvider'];
function emailConfig ($stateProvider) {
    // TODO: LILY-XXX: Clean up compose states and make email/template optional params
    $stateProvider.state('base.email.compose', {
        url: '/compose',
        views: {
            '@base.email': {
                templateUrl: '/messaging/email/compose/',
                controller: EmailComposeController,
                controllerAs: 'vm'
            }
        }
    });
    $stateProvider.state('base.email.composeEmail', {
        url: '/compose/{email}',
        views: {
            '@base.email': {
                templateUrl: '/messaging/email/compose/',
                controller: EmailComposeController,
                controllerAs: 'vm'
            }
        }
    });
    $stateProvider.state('base.email.composeEmailTemplate', {
        url: '/compose/{email}/{template}',
        views: {
            '@base.email': {
                templateUrl: '/messaging/email/compose/',
                controller: EmailComposeController,
                controllerAs: 'vm'
            }
        }
    });
    $stateProvider.state('base.email.draft', {
        url: '/draft/{id:[0-9]{1,}}',
        params: {
            messageType: 'draft'
        },
        views: {
            '@base.email': {
                templateUrl: function(elem, attr) {
                    return '/messaging/email/draft/' + elem.id + '/';
                },
                controller: EmailComposeController,
                controllerAs: 'vm'
            }
        }
    });
    $stateProvider.state('base.email.reply', {
        url: '/reply/{id:[0-9]{1,}}',
        params: {
            messageType: 'reply'
        },
        views: {
            '@base.email': {
                templateUrl: function(elem, attr) {
                    return '/messaging/email/reply/' + elem.id + '/';
                },
                controller: EmailComposeController,
                controllerAs: 'vm'
            }
        }
    });
    $stateProvider.state('base.email.replyAll', {
        // TODO: This should probably be redone so the url is nicer.
        // Maybe we can save the action in the scope?
        url: '/replyall/{id:[0-9]{1,}}',
        params: {
            messageType: 'reply-all'
        },
        views: {
            '@base.email': {
                templateUrl: function(elem, attr) {
                    return '/messaging/email/replyall/' + elem.id + '/';
                },
                controller: EmailComposeController,
                controllerAs: 'vm'
            }
        }
    });
    $stateProvider.state('base.email.forward', {
        url: '/forward/{id:[0-9]{1,}}',
        params: {
            messageType: 'forward'
        },
        views: {
            '@base.email': {
                templateUrl: function(elem, attr) {
                    return '/messaging/email/forward/' + elem.id + '/';
                },
                controller: EmailComposeController,
                controllerAs: 'vm'
            }
        }
    });
}

angular.module('app.email').controller('EmailComposeController', EmailComposeController);

EmailComposeController.$inject = ['$scope', '$state', '$stateParams', '$templateCache', '$q', 'ContactDetail', 'EmailMessage', 'EmailTemplate', 'SelectedEmailAccount'];
function EmailComposeController ($scope, $state, $stateParams, $templateCache, $q, ContactDetail, EmailMessage, EmailTemplate, SelectedEmailAccount) {
    var vm = this;

    $scope.conf.pageTitleBig = 'Send email';
    $scope.conf.pageTitleSmall = 'sending love through the world!';

    vm.discard = discard;

    activate();

    //////////

    function activate () {
        // Remove cache so new compose will always hit the server
        $templateCache.remove('/messaging/email/compose/');

        if ($stateParams.messageType == 'reply') {
            // If it's a reply, load the email message first
            EmailMessage.get({id: $stateParams.id}).$promise.then(function (emailMessage) {
                _initEmailCompose(emailMessage);
            });
        }
        else {
            // Otherwise just initialize the email compose
            _initEmailCompose();
        }
    }

    function _initEmailCompose(emailMessage) {
        var email = $stateParams.email;

        var promises = [];

        var recipient = null;
        var contactPromise;

        if (emailMessage) {
            contactPromise = ContactDetail.query({filterquery: 'email_addresses.email_address:' + emailMessage.sender.email_address}).$promise;
            promises.push(contactPromise);
        }
        else if (email) {
            contactPromise = ContactDetail.query({filterquery: 'email_addresses.email_address:' + email}).$promise;
            promises.push(contactPromise);
        }

        var emailTemplatePromise = EmailTemplate.query().$promise;
        promises.push(emailTemplatePromise);

        // TODO: LILY-XXX: Check if this can be cleaned up
        // Once all promises are done, continue
        $q.all(promises).then(function(results) {
            var templates;
            // This part should only be executed if we've loaded a contact
            if(contactPromise) {
                var contact = results[0][0];
                templates = results[1];

                if (emailMessage) {
                    email = emailMessage.sender.email_address;
                }

                if (contact) {
                    // The text which is actually used in the application/select2
                    var used_text = '"' + contact.name + '" <' + email + '>';
                    // The text shown in the recipient input
                    var displayed_text = contact.name + ' <' + email + '>';

                    recipient = {
                        id: used_text,
                        text: displayed_text,
                        object_id: contact.id
                    };
                } else {
                    recipient = {
                        id: email,
                        text: email,
                        object_id: null
                    };
                }
            } else {
                templates = results[0];
            }

            var template = $stateParams.template;
            // Determine whether the default template should be loaded or not
            var loadDefaultTemplate = template == undefined;

            // Set message type to given message type if available, otherwise set to message type 'new'
            var messageType = $stateParams.messageType ? $stateParams.messageType : 'new';

            HLInbox.init();
            HLInbox.initEmailCompose({
                templateList: templates,
                defaultEmailTemplateUrl: '/messaging/email/templates/get-default/',
                getTemplateUrl: '/messaging/email/templates/detail/',
                messageType: messageType,
                loadDefaultTemplate: loadDefaultTemplate,
                recipient: recipient,
                template: template
            });
            HLInbox.setSuccesURL($scope.previousState);
            if (SelectedEmailAccount.currentAccountId) {
                angular.element(HLInbox.config.emailAccountInput).select2('val', SelectedEmailAccount.currentAccountId);
            }
        });
    }

    function discard () {
        if ($scope.previousState) {
            window.location = $scope.previousState;
        } else {
            $state.go('base.email');
        }
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.email').config(emailConfig);
emailConfig.$inject = ['$stateProvider'];
function emailConfig ($stateProvider){
    $stateProvider.state('base.email.detail', {
        url: '/detail/{id:[0-9]{1,}}',
        views: {
            '@base.email': {
                templateUrl: 'email/controllers/detail.html',
                controller: EmailDetailController,
                controllerAs: 'vm'
            }
        }
    });
}

angular.module('app.email').controller('EmailDetail', EmailDetailController);

EmailDetailController.$inject = ['$scope', '$state', '$stateParams', 'EmailMessage', 'RecipientInformation', 'SelectedEmailAccount'];
function EmailDetailController ($scope, $state, $stateParams, EmailMessage, RecipientInformation, SelectedEmailAccount) {
    var vm = this;
    vm.displayAllRecipients = false;
    vm.message = null;
    vm.archiveMessage = archiveMessage;
    vm.trashMessage = trashMessage;
    vm.deleteMessage = deleteMessage;
    vm.toggleOverlay = toggleOverlay;
    vm.markAsUnread = markAsUnread;
    vm.onlyPlainText = false;

    $scope.conf.pageTitleBig = 'Email message';
    $scope.conf.pageTitleSmall = 'sending love through the world!';

    activate();

    //////

    function activate() {
        _getMessage();
    }

    function _getMessage() {
        EmailMessage.get({id: $stateParams.id}, function(result) {
            if (result.body_html) {
                result.bodyHTMLUrl = '/messaging/email/html/' + result.id + '/';
            }else{
                vm.onlyPlainText = true;
            }
            vm.message = result;
            // It's easier to iterate through a single array, so make an array with all recipients
            vm.message.all_recipients = result.received_by.concat(result.received_by_cc);
            // Get contacts
            RecipientInformation.getInformation(vm.message.all_recipients);

            if (!result.read) {
                EmailMessage.markAsRead($stateParams.id, true);
            }
            // Store current email account
            SelectedEmailAccount.setCurrentAccountId(vm.message.account);
        });
    }

    function archiveMessage() {
        EmailMessage.archive({id: vm.message.id}).$promise.then(function () {
            $state.go('base.email.list', { 'labelId': 'INBOX' });
        });
    }

    function trashMessage() {
        EmailMessage.trash({id: vm.message.id}).$promise.then(function () {
            $state.go('base.email.list', { 'labelId': 'INBOX' });
        });
    }

    function deleteMessage () {
        EmailMessage.delete({id: vm.message.id}).$promise.then(function () {
            $state.go('base.email.list', { 'labelId': 'INBOX' });
        });
    }

    function toggleOverlay () {
        vm.displayAllRecipients = !vm.displayAllRecipients;

        var $emailRecipients = $('.email-recipients');

        if (vm.displayAllRecipients) {
            $emailRecipients.height($emailRecipients[0].scrollHeight);
        } else {
            $emailRecipients.height('1.30em');
        }
    }

    function markAsUnread() {
        EmailMessage.markAsRead(vm.message.id, false).$promise.then(function () {
            $state.go('base.email.list', { 'labelId': 'INBOX' });
        });
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.email').config(emailConfig);
emailConfig.$inject = ['$stateProvider'];
function emailConfig($stateProvider) {
    $stateProvider.state('base.email.list', {
        url: '/all/{labelId}',
        views: {
            '@base.email': {
                templateUrl: 'email/controllers/email_list.html',
                controller: EmailListController,
                controllerAs: 'vm'
            }
        }
    });
    $stateProvider.state('base.email.accountAllList', {
        url: '/account/{accountId}/all',
        views: {
            '@base.email': {
                templateUrl: 'email/controllers/email_list.html',
                controller: EmailListController,
                controllerAs: 'vm'
            }
        }
    });
    $stateProvider.state('base.email.accountList', {
        url: '/account/{accountId}/{labelId}',
        views: {
            '@base.email': {
                templateUrl: 'email/controllers/email_list.html',
                controller: EmailListController,
                controllerAs: 'vm'
            }
        }
    });
}

angular.module('app.email').controller('EmailListController', EmailListController);

EmailListController.$inject = ['$location', '$scope', '$state', '$stateParams', 'EmailMessage', 'EmailLabel', 'EmailAccount', 'HLText', 'SelectedEmailAccount'];
function EmailListController ($location, $scope, $state, $stateParams, EmailMessage, EmailLabel, EmailAccount, HLText, SelectedEmailAccount) {
    var vm = this;
    vm.emailMessages = [];
    // Check if filter is set as query parameter
    vm.table = {
        page: 0,  // current page of pagination: 1-index
        pageSize: 20,  // number of items per page
        totalItems: 0, // total number of items
        filter: ''  // search filter
    };
    vm.opts = {
        checkboxesAll: false
    };
    vm.primaryEmailAccount = null;
    vm.setPage = setPage;
    vm.toggleCheckboxes = toggleCheckboxes;
    vm.showReplyOrForwardButtons = showReplyOrForwardButtons;
    vm.replyOnMessage = replyOnMessage;
    vm.replyAllOnMessage = replyAllOnMessage;
    vm.forwardOnMessage = forwardOnMessage;
    vm.markAsRead = markAsRead;
    vm.markAsUnread = markAsUnread;
    vm.archiveMessages = archiveMessages;
    vm.trashMessages = trashMessages;
    vm.deleteMessages = deleteMessages;
    vm.moveMessages = moveMessages;
    vm.reloadMessages = reloadMessages;
    vm.goToDraft = goToDraft;

    $scope.conf.pageTitleBig = 'Email';
    $scope.conf.pageTitleSmall = 'sending love through the world!';

    activate();

    ///////

    function activate() {
        vm.table.filter = $location.search().search || '';
        watchTable();
        // Store current email account
        SelectedEmailAccount.setCurrentAccountId($stateParams.accountId);
        SelectedEmailAccount.setCurrentFolderId($stateParams.labelId);
    }

    function watchTable() {
        // Check for search input and pagination
        $scope.$watchGroup([
            'vm.table.filter',
            'vm.table.page'
        ], function (newValues, oldValues) {
            // Reset page if we start searching
            if (oldValues[0] == "" && newValues[0] != "") {
                vm.setPage(0);
            }
            _reloadMessages();
        });
    }

    function setPage(pageNumber) {
        if (pageNumber >= 0 && pageNumber * vm.table.pageSize < vm.table.totalItems) {
            vm.table.page = pageNumber;
        }
    }


    function toggleCheckboxes () {
        for (var i in vm.emailMessages) {
            vm.emailMessages[i].checked = vm.opts.checkboxesAll;
        }
    }

    function _toggleReadMessages(read) {
        for (var i in vm.emailMessages) {
            if (vm.emailMessages[i].checked) {
                EmailMessage.markAsRead(vm.emailMessages[i].id, read);
                vm.emailMessages[i].read = read;
            }
        }
    }

    /**
     * Only show the reply and forward buttons if there is one message checked.
     */
    function showReplyOrForwardButtons () {
        var number = 0;
        for (var i in vm.emailMessages) {
            if (vm.emailMessages[i].checked) {
                number++;
                if (number > 1) {
                    return false;
                }
            }
        }
        return number == 1;
    }

    /**
     * Get the currently selected EmailMessage instance.
     *
     * @returns EmailMessage instance
     */
    function _selectedMessage() {
        for (var i in vm.emailMessages) {
            if (vm.emailMessages[i].checked) {
                return vm.emailMessages[i];
            }
        }
    }

    /**
     * Reply on selected message.
     */
    function replyOnMessage() {
        var message = _selectedMessage();
        if (message) {
            $state.go('base.email.reply', {id: message.id});
        }
    }

    /**
     * Reply-all on selected message.
     */
    function replyAllOnMessage () {
        var message = _selectedMessage();
        if (message) {
            $state.go('base.email.replyAll', {id: message.id});
        }
    }

    /**
     * Forward on selected message.
     */
    function forwardOnMessage () {
        var message = _selectedMessage();
        if (message) {
            $state.go('base.email.forward', {id: message.id});
        }
    }

    function markAsRead () {
        _toggleReadMessages(true);
    }

    function markAsUnread() {
        _toggleReadMessages(false);
    }

    function _removeCheckedMessagesFromList() {
        var i = vm.emailMessages.length;
        while (i--) {
            if (vm.emailMessages[i].checked) {
                vm.emailMessages.splice(i, 1);
            }
        }
    }

    function archiveMessages () {
        for (var i in vm.emailMessages) {
            if (vm.emailMessages[i].checked) {
                EmailMessage.archive({id: vm.emailMessages[i].id});
            }
        }
        _removeCheckedMessagesFromList();
    }

    function trashMessages () {
        for (var i in vm.emailMessages) {
            if (vm.emailMessages[i].checked) {
                EmailMessage.trash({id: vm.emailMessages[i].id});
            }
        }
        _removeCheckedMessagesFromList();
    }

    function deleteMessages () {
        for (var i in vm.emailMessages) {
            if (vm.emailMessages[i].checked) {
                EmailMessage.delete({id: vm.emailMessages[i].id});
            }
        }
        _removeCheckedMessagesFromList();
    }

    function moveMessages (labelId) {
        var removedLabels = [];
        if (vm.label.label_id) {
            removedLabels = [vm.label.label_id];
        }
        var addedLabels = [labelId];
        // Gmail API needs to know the new labels as well as the old ones, so send them too
        var data = {
            remove_labels: removedLabels,
            add_labels: addedLabels
        };
        for (var i in vm.emailMessages) {
            if (vm.emailMessages[i].checked) {
                EmailMessage.move({id: vm.emailMessages[i].id, data: data});
            }
        }
        _removeCheckedMessagesFromList();
    }

    function reloadMessages () {
        vm.emailMessages = [];
        _reloadMessages();
    }

    function goToDraft (messageId) {
        window.open('/messaging/email/draft/' + messageId + '/', '_self');
    }

    function _reloadMessages() {
        var filterquery = [];

        if ($stateParams.labelId) {
            filterquery.push('label_id:' + $stateParams.labelId);
        } else {
            filterquery.push('NOT label_id:Sent');
        }

        if ($stateParams.accountId) {
            filterquery.push('account:' + $stateParams.accountId);

            if ($stateParams.labelId) {
                // Get the label for the given accountId
                EmailLabel.query({
                    label_id: $stateParams.labelId,
                    account__id: $stateParams.accountId
                }, function (results) {
                    if (results.length) {
                        vm.label = results[0];
                        vm.label.name = vm.label.name.hlCapitalize();
                    } else {
                        vm.label = {id: $stateParams.labelId, name: $stateParams.labelId.hlCapitalize()};
                    }
                });
            }
            // Get the account for the given accountId
            vm.account = EmailAccount.get({id: $stateParams.accountId});
        } else {
            vm.label = {id: $stateParams.labelId, name: $stateParams.labelId.hlCapitalize()};
        }

        if ($stateParams.labelId && $stateParams.labelId != 'TRASH') {
            filterquery.push('is_removed:false');
        }

        if (filterquery) {
            filterquery = filterquery.join(' AND ');
        }

        EmailMessage.search({
            filterquery: filterquery,
            q: vm.table.filter,
            size: vm.table.pageSize,
            page: vm.table.page
        }, function (data) {
            vm.emailMessages = data.hits;
            vm.table.totalItems = data.total;
        });
    }
}


})(angular);
(function(angular){
'use strict';
angular.module('app.email').controller('LabelListController', LabelListController);

LabelListController.$inject = ['$filter', '$interval', '$scope', 'EmailAccount', 'primaryEmailAccountId'];
function LabelListController ($filter, $interval, $scope, EmailAccount, primaryEmailAccountId) {
    var vm = this;
    vm.accountList = [];
    vm.primaryEmailAccountId = primaryEmailAccountId;
    vm.labelCount = 0;
    vm.hasUnreadLabel = hasUnreadLabel;
    vm.unreadCountForLabel = unreadCountForLabel;

    activate();

    //////////

    function activate() {
        _startIntervalAccountInfo();
    }

    function _startIntervalAccountInfo() {
        _getAccountInfo();
        var stopGetAccountInfo = $interval(_getAccountInfo, 60000);

        // Stop fetching when out of scope
        $scope.$on('$destroy', function() {
            // Make sure that the interval is destroyed too
            if (angular.isDefined(stopGetAccountInfo)) {
                $interval.cancel(stopGetAccountInfo);
                stopGetAccountInfo = undefined;
            }
        });
    }

    // Fetch the EmailAccounts & associated labels
    function _getAccountInfo () {
        EmailAccount.mine(function (results) {
            // Sort accounts on id
            results = $filter('orderBy')(results, 'id');

            vm.accountList = [];
            // Make sure primary account is set first
            angular.forEach(results, function(account) {
                if (account.id != vm.primaryEmailAccountId) {
                    this.push(account);
                } else {
                    this.unshift(account);
                }
            }, vm.accountList);

            // Check for unread email count
            var labelCount = {};
            for (var i in vm.accountList) {
                for (var j in vm.accountList[i].labels) {
                    var label = vm.accountList[i].labels[j];
                    if (label.label_type == 0) {
                        if (labelCount.hasOwnProperty(label.label_id)) {
                            labelCount[label.label_id] += parseInt(label.unread);
                        } else {
                            labelCount[label.label_id] = parseInt(label.unread);
                        }
                    }
                }
            }
            vm.labelCount = labelCount;
        });
    }

    function unreadCountForLabel(account, labelId) {
        var count = 0;
        angular.forEach(account.labels, function(label) {
            if (label.label_id == labelId) {
                count = label.unread;
                return true
            }
        });
        return count;
    }

    function hasUnreadLabel (account, labelId) {
        return unreadCountForLabel(account, labelId) > 0;

    }
}

})(angular);
(function(angular){
'use strict';
/**
 * contactIcon Directive shows how the email is connected with an account or contact
 *
 * @param message object: object with message info
 *
 * Example:
 *
 * <td contact-icon message="message"></td>
 *
 */
angular.module('app.email.directives').directive('contactIcon', contactIcon);

contactIcon.$inject = ['$http'];
function contactIcon ($http) {
    return {
        restrict: 'A',
        scope: {
            message: '='
        },
        replace: true,
        templateUrl: 'email/directives/contact_icon.html',
        link: function (scope, element, attrs) {

            // Do we have an associated account or contact?
            if (scope.message.sender_email) {
                $http.get('/search/emailaddress/' + scope.message.sender_email)
                    .success(function (data) {
                        scope.emailAddressResults = data;
                        if (data.type == 'contact') {
                            // Contact and has account
                            if (data.data.accounts) {
                                scope.status = 'complete';
                                // Contact without account
                            } else {
                                scope.status = 'needsAccount';
                            }
                        } else if (data.type == 'account') {
                            // Is the emailadress from the account it self (eg. info@)
                            if (data.complete) {
                                scope.status = 'complete';
                            } else {
                                scope.status = 'needsContact';
                            }
                        } else {
                            scope.status = 'needsEverything';
                        }
                    });
            } else {
                scope.status = 'complete';
            }
        }
    };
}

})(angular);
(function(angular){
'use strict';
angular.module('app.email.directives').directive('sendAndArchive', SendAndArchiveDirective);

SendAndArchiveDirective.$inject = ['SelectedEmailAccount'];
function SendAndArchiveDirective (SelectedEmailAccount) {
    return {
        restrict: 'A',
        link: function (scope, element) {
            element.on('click', function () {
                $('<input />').attr('type', 'hidden')
                    .attr('name', 'archive')
                    .attr('value', true)
                    .appendTo(element.closest('form'));
                if (SelectedEmailAccount.currentAccountId && SelectedEmailAccount.currentFolderId) {
                    $("input[name='success_url']").val('#/email/account/' + SelectedEmailAccount.currentAccountId + '/' + SelectedEmailAccount.currentFolderId);
                }
            });
        }
    }
}


})(angular);
(function(angular){
'use strict';
angular.module('app.email.directives').directive('sendChecker', sendCheckerDirective);

function sendCheckerDirective () {
    return {
        restrict: 'A',
        link: function (scope, element) {
            element.on('click', function (event) {
                // check recipients
                if (!$('#id_send_to_normal').val() && !$('#id_send_to_cc').val() && !$('#id_send_to_bcc').val()) {
                    event.stopPropagation();
                    event.preventDefault();
                    bootbox.alert('I couldn\'t find a recipient, could you please fill in where I need to send this mail.');
                    return;
                }

                // check subject
                var subject = angular.element('#id_subject').val();
                if (subject == "") {
                    event.stopPropagation();
                    event.preventDefault();
                    bootbox.dialog({
                        message: 'Are you sure you want to send this email without a subject?',
                        title: 'No Subject',
                        buttons: {
                            danger: {
                                label: 'Oops, I\'ll fix it',
                                className: 'btn-danger'
                            },
                            success: {
                                label: 'No Problem, send it anyway',
                                className: 'btn-success',
                                callback: function () {
                                    HLInbox.submitForm('submit-send', element.closest('form')[0]);
                                }
                            }
                        }
                    });
                }
            });
        }
    }
}


})(angular);
(function(angular){
'use strict';
angular.module('app.email.services').factory('EmailAccount', EmailAccount);

EmailAccount.$inject = ['$resource'];
function EmailAccount ($resource) {
    return $resource('/api/messaging/email/account/:id/', null,
        {
            'update': { method: 'PUT' },
            'shareWith': {
                method: 'POST',
                url: '/api/messaging/email/account/:id/shared/'
            },
            'mine': {
                method: 'GET',
                url: '/api/messaging/email/account/mine/',
                isArray: true
            }
        }
    );
}

})(angular);
(function(angular){
'use strict';
angular.module('app.email.services').factory('EmailDetail', EmailDetail);

EmailDetail.$inject = ['$resource'];
function EmailDetail ($resource) {
    return $resource(
        '',
        {size:100},
        {
            query: {
                url: '/search/search/?type=email_emailmessage&size=:size&sort=-sent_date&filterquery=:filterquery&account_related=:account_related',
                isArray: true,
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    var objects = [];
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function(obj) {
                            obj = $.extend(obj, {historyType: 'email', color: 'green', date: obj.sent_date, right: false});
                            objects.push(obj)
                        });
                    }
                    return objects;
                }
            }
        }
    );
}

})(angular);
(function(angular){
'use strict';
angular.module('app.email.services').factory('EmailLabel', EmailLabel);

EmailLabel.$inject = ['$resource'];
function EmailLabel ($resource) {
    return $resource('/api/messaging/email/label/:id/');
}

})(angular);
(function(angular){
'use strict';
angular.module('app.email.services').factory('EmailMessage', EmailMessage);

EmailMessage.$inject = ['$resource', '$q'];
function EmailMessage ($resource, $q) {
    var EmailMessage = $resource(
        '/api/messaging/email/email/:id/:actions',
        {},
        {
            'update': {
                method: 'PUT',
                params: {
                    id: '@id',
                    actions: ''
                }
            },
            'delete': {
                method: 'DELETE',
                params: {
                    id: '@id',
                    actions: ''
                }
            },
            'archive': {
                method: 'PUT',
                params: {
                    id: '@id',
                    actions: 'archive'
                }
            },
            'trash': {
                method: 'PUT',
                params: {
                    id: '@id',
                    actions: 'trash'
                }
            },
            'get': {
                method: 'GET',
                params: {
                    id: '@id',
                    actions: ''
                }
            },
            'move': {
                method: 'PUT',
                params: {
                    id: '@id',
                    actions: 'move'
                }
            },
            'search': {
                method: 'GET',
                url: '/search/search/',
                params: {
                    user_email_related: 1,
                    type: 'email_emailmessage',
                    sort: '-sent_date',
                    size: 20
                }
            }
        }
    );

    EmailMessage.markAsRead = markAsRead;
    EmailMessage.getDashboardMessages = getDashboardMessages;

    //////

    function markAsRead (id, read) {
        return this.update({id: id, read: read});
    }

    function getDashboardMessages (field, sorting) {
        var filterQuery = ['read:false AND label_id:INBOX'];
        var sort = '';
        sort += sorting ? '-': '';
        sort += field;

        var deferred = $q.defer();
        EmailMessage.search({
            filterquery: filterQuery,
            sort: sort
        }, function (data) {
            deferred.resolve(data.hits);
        });
        return deferred.promise;
    }
    return EmailMessage
}

})(angular);
(function(angular){
'use strict';
angular.module('app.email.services').factory('EmailTemplate', EmailTemplate);

EmailTemplate.$inject = ['$resource'];
function EmailTemplate ($resource) {
    return $resource('/api/messaging/email/emailtemplate/:id/');
}

})(angular);
(function(angular){
'use strict';
angular.module('app.email.services').factory('RecipientInformation', RecipientInformation);

RecipientInformation.$inject = ['$http'];
function RecipientInformation ($http) {

    var RecipientInformation = {};

    RecipientInformation.getInformation = getInformation;

    //////

    function getInformation(recipients) {
        recipients.forEach(function (recipient) {
            // If there's a name set, try to get the contact id
            // Don't set/change the name because we want to keep the original email intact
            if (recipient.name != '') {
                $http.get('/search/emailaddress/' + recipient.email_address)
                    .success(function (data) {
                        if (data.type == 'contact') {
                            if (data.data.id) {
                                recipient.contact_id = data.data.id;
                            }
                        }
                    });
            }
        });
    }

    return RecipientInformation;
}

})(angular);
(function(angular){
'use strict';
angular.module('app.email.services').factory('SelectedEmailAccount', SelectedEmailAccount);

function SelectedEmailAccount () {

    var factory = {
        currentAccountId: null,
        setCurrentAccountId: setCurrentAccountId,
        currentFolderId: null,
        setCurrentFolderId: setCurrentFolderId
    };
    return factory;

    function setCurrentAccountId (accountId) {
        factory.currentAccountId = accountId;
    }

    function setCurrentFolderId (folderId) {
        factory.currentFolderId = folderId;
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.notes').factory('Note', Note);

Note.$inject = ['$resource'];
function Note ($resource) {
    return $resource('/api/notes/:id/');
}

})(angular);
(function(angular){
'use strict';
angular.module('app.notes').factory('NoteDetail', NoteDetail);

NoteDetail.$inject = ['$resource'];
function NoteDetail ($resource) {
    return $resource(
        '/search/search/?type=notes_note&filterquery=id\::id',
        {size:100},
        {
            get: {
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    if (data && data.hits && data.hits.length > 0) {
                        var obj = data.hits[0];
                        return obj;
                    }
                    return null;
                }
            },
            query: {
                url: '/search/search/?type=notes_note&size=:size&sort=-date&filterquery=:filterquery',
                isArray: true,
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    var objects = [];
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function(obj) {
                            obj = $.extend(obj, {historyType: 'note', color: 'yellow'});
                            objects.push(obj)
                        });
                    }
                    return objects;
                }
            },
            totalize: {
                url: '/search/search/?type=notes_note&size=0&filterquery=:filterquery',
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    if (data && data.total) {
                        return {total: data.total};
                    }
                    return {total: 0};
                }
            }
        }
    );
}

})(angular);
(function(angular){
'use strict';
angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig ($stateProvider) {
    $stateProvider.state('base.preferences', {
        url: '/preferences',
        abstract: true,
        views: {
            '@': {
                templateUrl: 'preferences/controllers/base.html',
                controller: PreferencesBase,
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: 'Preferences'
        }
    });
}

angular.module('app.preferences').controller('PreferencesBase', PreferencesBase);

PreferencesBase.$inject = ['$scope'];
function PreferencesBase ($scope) {
    $scope.conf.pageTitleBig = 'Preferences';
    $scope.conf.pageTitleSmall = 'configure your mayhem';
}

})(angular);
(function(angular){
'use strict';
angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.emailaccounts.edit', {
        url: '/edit/{id:[0-9]{1,}}',
        views: {
            '@base.preferences': {
                templateUrl: function (elem, attr) {
                    return 'messaging/email/accounts/update/' + elem.id;
                },
                controller: 'PreferencesEmailAccountEdit'
            }
        },
        ncyBreadcrumb: {
            label: 'Edit EmailAccount'
        }
    });
}

angular.module('app.preferences').controller('PreferencesEmailAccountEdit', PreferencesEmailAccountEdit);

function PreferencesEmailAccountEdit () {}

})(angular);
(function(angular){
'use strict';
angular.module('app.preferences').config(emailPreferencesStates);

emailPreferencesStates.$inject = ['$stateProvider'];
function emailPreferencesStates($stateProvider) {
    $stateProvider.state('base.preferences.emailaccounts', {
        url: '/emailaccounts',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/controllers/emailaccount_list.html',
                controller: PreferencesEmailAccountList,
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: 'Email Account'
        },
        resolve: {
            ownedAccounts: ['EmailAccount', function (EmailAccount) {
                return EmailAccount.query({owner: currentUser.id}).$promise;
            }],
            sharedAccounts: ['EmailAccount', function (EmailAccount) {
                return EmailAccount.query({shared_with_users__id: currentUser.id}).$promise;
            }],
            publicAccounts: ['EmailAccount', function (EmailAccount) {
                return EmailAccount.query({public: "True"}).$promise;
            }],
            user: ['User', function (User) {
                return User.me().$promise;
            }]
        }
    });
}

angular.module('app.preferences').controller('PreferencesEmailAccountList', PreferencesEmailAccountList);

PreferencesEmailAccountList.$inject =['$modal', 'EmailAccount', 'User', 'ownedAccounts', 'sharedAccounts', 'publicAccounts', 'user'];
function PreferencesEmailAccountList($modal, EmailAccount, User, ownedAccounts, sharedAccounts, publicAccounts, user) {

    var vm = this;
    vm.ownedAccounts = ownedAccounts;
    vm.sharedAccounts = sharedAccounts;
    vm.publicAccounts = publicAccounts;
    vm.currentUser = user;
    vm.activate = activate;
    vm.deleteAccount = deleteAccount;
    vm.openShareAccountModal = openShareAccountModal;
    vm.makePrimaryAccount = makePrimaryAccount;

    activate();

    ////////

    function activate() {}

    // Get relevant accounts
    function loadAccounts() {
        // Accounts owned
        EmailAccount.query({owner: vm.currentUser.id}, function(data) {
            vm.ownedAccounts = data;
        });

        // Accounts shared with user
        EmailAccount.query({shared_with_users__id: vm.currentUser.id}, function(data) {
            vm.sharedAccounts = data;
        });

        // Accounts public
        EmailAccount.query({public: "True"}, function(data) {
            vm.publicAccounts = data;
        });
    }

    function deleteAccount (accountId) {
        if (confirm('sure to delete?')) {
            EmailAccount.delete({id: accountId}, function() {
                // Reload accounts
                loadAccounts();
            });
        }
    }

    function openShareAccountModal (emailAccount) {
        var modalInstance = $modal.open({
            templateUrl: 'preferences/controllers/emailaccount_share.html',
            controller: 'EmailAccountShareModalController',
            size: 'lg',
            resolve: {
                currentAccount: function() {
                    return emailAccount;
                }
            }
        });

        modalInstance.result.then(function () {
            loadAccounts();
        }, function() {
            loadAccounts();
        });
    }

    function makePrimaryAccount (emailAccount) {
        vm.currentUser.primary_email_account = emailAccount.id;
        User.update({id: 'me'}, vm.currentUser);
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.preferences').controller('EmailAccountShareModalController', EmailAccountShareModalController);

EmailAccountShareModalController.$inject = ['$modalInstance', '$scope', 'EmailAccount', 'User', 'currentAccount'];
function EmailAccountShareModalController ($modalInstance, $scope, EmailAccount, User, currentAccount) {
    $scope.currentAccount = currentAccount;

    // Get all users to display in a list
    User.query({}, function(data) {
        $scope.users = [];
        // Check if user has the emailaccount already shared
        angular.forEach(data, function(user) {
            if ($scope.currentAccount.shared_with_users.indexOf(user.id) !== -1) {
                user.sharedWith = true;
            }
            $scope.users.push(user);
        });
    });

    $scope.ok = function () {
        // Save updated account information
        if ($scope.currentAccount.public) {
            EmailAccount.update({id: $scope.currentAccount.id}, $scope.currentAccount, function() {
                $modalInstance.close();
            });
        } else {
            // Get ids of the users to share with
            var shared_with_users = [];
            angular.forEach($scope.users, function(user) {
                if(user.sharedWith) {
                    shared_with_users.push(user.id);
                }
            });
            // Push ids to api
            EmailAccount.shareWith({id: $scope.currentAccount.id}, {shared_with_users: shared_with_users}, function() {
                $modalInstance.close();
            });
        }
    };

    // Lets not change anything
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
}

})(angular);
(function(angular){
'use strict';
angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.emailtemplates.create', {
        url: '/create',
        views: {
            '@base.preferences': {
                templateUrl: '/messaging/email/templates/create/',
                controller: PreferencesEmailTemplatesCreate
            }
        },
        ncyBreadcrumb: {
            label: 'Email template edit'
        }
    });
}

angular.module('app.preferences').controller('PreferencesEmailTemplatesCreate', PreferencesEmailTemplatesCreate);

// TODO: LILY-XXX: Try to change the openVariable and closeVariable to curly braces, so it's consistent with other templating engines
function PreferencesEmailTemplatesCreate () {
    HLInbox.init();
    HLInbox.initWysihtml5();
    HLEmailTemplates.init({
        parseEmailTemplateUrl: '',
        openVariable: '[[',
        closeVariable: ']]'
    });
}

})(angular);
(function(angular){
'use strict';
angular.module('app.preferences').controller('PreferencesSetTemplateDefaultModal', PreferencesSetTemplateDefaultModal);

PreferencesSetTemplateDefaultModal.$inject = ['$http', '$modalInstance', '$scope', 'emailTemplate'];
function PreferencesSetTemplateDefaultModal ($http, $modalInstance, $scope, emailTemplate) {
    $scope.emailTemplate = emailTemplate;

    $scope.ok = function () {
        $http({
            url: '/messaging/email/templates/set-default/' + $scope.emailTemplate.id + '/',
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            data: $.param({id: $scope.emailTemplate.id})
        }).success(function() {
            $modalInstance.close($scope.emailTemplate);
        });
    };

    // Lets not change anything
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
}

})(angular);
(function(angular){
'use strict';
angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.emailtemplates.edit', {
        url: '/edit/{id:[0-9]{1,}}',
        views: {
            '@base.preferences': {
                templateUrl: function(elem, attr) {
                    return '/messaging/email/templates/update/' + elem.id +'/';
                },
                controller: PreferencesEmailTemplatesEdit
            }
        },
        ncyBreadcrumb: {
            label: 'Email template edit'
        }
    });
}

angular.module('app.preferences').controller('PreferencesEmailTemplatesEdit', PreferencesEmailTemplatesEdit);

// TODO: LILY-XXX: Try to change the openVariable and closeVariable to curly braces, so it's consistent with other templating engines
function PreferencesEmailTemplatesEdit () {
    HLInbox.init();
    HLInbox.initWysihtml5();
    HLEmailTemplates.init({
        parseEmailTemplateUrl: '',
        openVariable: '[[',
        closeVariable: ']]'
    });
}


})(angular);
(function(angular){
'use strict';
angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.emailtemplates', {
        url: '/emailtemplates',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/controllers/emailtemplate_list.html',
                controller: PreferencesEmailTemplatesList
            }
        },
        ncyBreadcrumb: {
            label: 'Email templates'
        }
    });
}

angular.module('app.preferences').controller('PreferencesEmailTemplatesList', PreferencesEmailTemplatesList);

PreferencesEmailTemplatesList.$inject = ['$modal', '$scope', 'EmailTemplate'];
function PreferencesEmailTemplatesList ($modal, $scope, EmailTemplate) {
    //$scope.conf.pageTitleBig = 'EmailTemplate settings';
    //$scope.conf.pageTitleSmall = 'the devil is in the details';

    EmailTemplate.query({}, function(data) {
        $scope.emailTemplates = data;
    });

    $scope.makeDefault = function(emailTemplate) {
        // TODO: LILY-756: Make this controller more Angular
        var modalInstance = $modal.open({
            templateUrl: '/messaging/email/templates/set-default/' + emailTemplate.id + '/',
            controller: 'PreferencesSetTemplateDefaultModal',
            size: 'lg',
            resolve: {
                emailTemplate: function () {
                    return emailTemplate;
                }
            }
        });

        modalInstance.result.then(function () {
            $state.go($state.current, {}, {reload: false});
        }, function () {
        });
    };

    $scope.deleteEmailTemplate = function(emailtemplate) {
        if (confirm('Are you sure?')) {
            EmailTemplate.delete({
                id: emailtemplate.id
            }, function() {  // On success
                var index = $scope.emailTemplates.indexOf(emailtemplate);
                $scope.emailTemplates.splice(index, 1);
            }, function(error) {  // On error
                alert('something went wrong.')
            })
        }
    };
}

})(angular);
(function(angular){
'use strict';
angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig ($stateProvider) {
    $stateProvider.state('base.preferences.user.account', {
        url: '/account',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/user/account/',
                controller: PreferencesUserAccountController,
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: 'account'
        }
    });
}

/**
 * PreferencesUserAccount is a controller to show the user account page.
 */
angular.module('app.preferences').controller('PreferencesUserAccountController', PreferencesUserAccountController);

PreferencesUserAccountController.$inject = ['$scope'];
function PreferencesUserAccountController ($scope) {
    $scope.$on('$viewContentLoaded', function() {
        djangoPasswordStrength.initListeners();
    });
}

})(angular);
(function(angular){
'use strict';
angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig ($stateProvider) {
    $stateProvider.state('base.preferences.user.token', {
        url: '/token',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/controllers/user_apitoken.html',
                controller: UserTokenController,
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: 'account'
        }
    });
}

/**
 * PreferencesUserProfile is a controller to show the user profile page.
 */
angular.module('app.preferences').controller('UserTokenController', UserTokenController);

UserTokenController.$inject = ['User'];
function UserTokenController (User) {
    var vm = this;
    vm.token = '';

    vm.deleteToken = deleteToken;
    vm.generateToken = generateToken;

    activate();

    /////

    function activate() {
        // Get the token of the current user
        User.token(function(data) {
            if (data.auth_token) {
                vm.token = data.auth_token;
            } else {
                vm.token = '';
            }
        });
    }

    function deleteToken () {
        // Get the token of the current user
        User.deleteToken(function() {
            vm.token = '';
            toastr.success('And it\'s gone!', 'Token deleted')
        });
    }

    function generateToken() {
        // Get the token of the current user
        User.generateToken({},function(data) {
            vm.token = data.auth_token;
            toastr.success('I\'ve created a new one', 'Token generated')
        });
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig ($stateProvider) {
    $stateProvider.state('base.preferences.user', {
        url: '/user',
        abstract: true,
        ncyBreadcrumb: {
            label: 'user'
        }
    });
}

})(angular);
(function(angular){
'use strict';
angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig ($stateProvider) {
    $stateProvider.state('base.preferences.user.profile', {
        url: '/profile',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/user/profile/',
                controller: PreferencesUserProfileController,
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: 'profile'
        }
    });
}

angular.module('app.preferences').controller('PreferencesUserProfile', PreferencesUserProfileController);
function PreferencesUserProfileController () {}

})(angular);
(function(angular){
'use strict';
 angular.module('app.users.filters').filter('fullName', fullName);

 function fullName () {
    return function(user) {
        return [user.first_name, user.preposition, user.last_name].join(' ');
    };
}

})(angular);
(function(angular){
'use strict';
angular.module('app.users.services').factory('User', User);

User.$inject = ['$resource'];
function User ($resource) {
    return $resource('/api/users/user/', null, {
        me: {
            method: 'GET',
            url: '/api/users/user/me/',
            isArray: false
        },
        update: {
            method: 'PUT',
            url: '/api/users/user/:id/'
        },
        token: {
            method: 'GET',
            url: '/api/users/user/token/'
        },
        deleteToken: {
            method: 'DELETE',
            url: '/api/users/user/token/'
        },
        generateToken: {
            method: 'POST',
            url: '/api/users/user/token/'
        }
    });
}

})(angular);
(function(angular){
'use strict';
angular.module('app.users.services').factory('UserTeams', UserTeams);

UserTeams.$inject = ['$resource'];
function UserTeams ($resource) {
    return $resource('/api/users/team/', null, {
        mine: {
            method: 'GET',
            url: '/api/users/team/mine/',
            isArray: true
        }
    });
}

})(angular);
(function(angular){
'use strict';
angular.module('app.utils').controller('EditNoteModalController', EditNoteModalController);

EditNoteModalController.$inject = ['$http', '$modalInstance', '$scope', 'note'];
function EditNoteModalController($http, $modalInstance, $scope, note) {
    $scope.note = note;
    $scope.ok = function () {
        $http({
            url: '/notes/update/' + $scope.note.id + '/',
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            data: $.param({content: $scope.note.content, type: $scope.note.type})
        }).success(function() {
            $modalInstance.close($scope.note);
        });
    };

    // Lets not change anything
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
}

})(angular);
(function(angular){
'use strict';
angular.module('app.utils.directives').directive('collapsable', CollapsableDirective);

CollapsableDirective.$inject = [];
function CollapsableDirective () {
    return {
        restrict: 'E',
        transclude: true,
        templateUrl: 'utils/directives/collapsable.html',
        controller: CollapsableController,
        controllerAs: 'cl',
        bindToController: true,
        scope: {
            name: '@'
        }
    }
}

CollapsableController.$inject = ['$scope', 'Cookie'];
function CollapsableController ($scope, Cookie) {
    var vm = this;

    var cookie = Cookie('collapseDirective-' + vm.name);
    vm.folded = cookie.get('folded', false);

    vm.toggleFolded = toggleFolded;

    function toggleFolded () {
        vm.folded = !vm.folded;
        cookie.put('folded', vm.folded);
        $scope.$broadcast('foldedToggle', vm.folded);
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.utils.directives').directive('collapsableButton', CollapsableButtonDirective);

CollapsableButtonDirective.$inject = [];
function CollapsableButtonDirective () {
    return {
        restrict: 'E',
        require: '^collapsable',
        templateUrl: 'utils/directives/collapsable_button.html',
        link: function(scope, element, attrs, collapsableCtrl) {
            element.on('click', function () {
                collapsableCtrl.toggleFolded();
            });
        },
        controller: CollapsableButtonController,
        controllerAs: 'vm'
    }
}

CollapsableButtonController.$inject = ['$scope'];
function CollapsableButtonController ($scope) {
    var vm = this;
    // Don't know why, but this controller is instantiated without the parent directive sometimes, somewhere...
    vm.folded = $scope.$parent.cl ? $scope.$parent.cl.folded : false;

    $scope.$on('foldedToggle', function (event, folded) {
        vm.folded = folded;
        $scope.$apply();
    });
}

})(angular);
(function(angular){
'use strict';
angular.module('app.utils.directives').directive('collapsableContent', CollapsableContentDirective);

CollapsableContentDirective.$inject = [];
function CollapsableContentDirective () {
    return {
        restrict: 'E',
        templateUrl: 'utils/directives/collapsable_content.html',
        transclude: true,
        require: '^collapsable',
        controller: CollapsableContentController,
        controllerAs: 'vm'
    }
}

CollapsableContentController.$inject = ['$scope'];
function CollapsableContentController ($scope) {
    var vm = this;
    // Don't know why, but this controller is instantiated without the parent directive sometimes, somewhere...
    vm.folded = $scope.$parent.cl ? $scope.$parent.cl.folded : false;

    $scope.$on('foldedToggle', function (event, folded) {
        vm.folded = folded;
        $scope.$apply();
    });
}

})(angular);
(function(angular){
'use strict';
angular.module('app.utils.directives').directive('historyAddNote', historyAddNoteDirective);

function historyAddNoteDirective () {
    return {
        restrict: 'E',
        scope: {
            item: '='
        },
        templateUrl: 'utils/directives/history_add_note.html',
        controller: HistoryAddNoteController,
        controllerAs: 'vm',
        bindToController: true
    }
}

HistoryAddNoteController.$inject = ['$http', '$state'];
function HistoryAddNoteController ($http, $state) {
    var vm = this;

    vm.addNote = addNote;

    //////

    function addNote () {
        $http({
            method: 'POST',
            url: '/notes/create/',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            data: $.param({
                content: vm.note,
                type: 0,
                content_type: vm.item.historyType,
                object_id: vm.item.id
            })
        }).success(function() {
            $state.go($state.current, {}, {reload: true});
        });
    }
}

})(angular);
(function(angular){
'use strict';
angular.module('app.utils.directives').directive('historyList', HistoryListDirective);

HistoryListDirective.$inject = ['$filter', '$http', '$modal', '$q', '$state', 'EmailAccount', 'Note', 'NoteDetail', 'CaseDetail', 'DealDetail','EmailDetail'];
function HistoryListDirective ($filter, $http, $modal, $q, $state, EmailAccount, Note, NoteDetail, CaseDetail, DealDetail, EmailDetail) {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            target: '=',
            object: '='
        },
        templateUrl: 'utils/directives/historylist.html',
        link: function (scope, element, attrs) {
            var noteTargets = ['account', 'contact', 'deal', 'case'];
            var caseTargets = ['account', 'contact'];
            var dealTargets = ['account'];
            var emailTargets = ['account', 'contact'];
            var page = 0;
            var pageSize = 15;

            scope.history = {};
            scope.history.list = [];
            scope.history.types = {
                '': {name: 'All', visible: true},
                'note': {name: 'Notes', visible: false},
                'case': {name: 'Cases',visible: false},
                'deal': {name: 'Deals', visible: false},
                'email': {name: 'Emails', visible: false}
            };
            scope.history.activeFilter = '';
            scope.history.showMoreText = 'Show more';
            scope.history.loadMore = loadMore;
            scope.history.reloadHistory = reloadHistory;
            scope.history.addNote = addNote;
            scope.history.editNote = editNote;
            scope.history.deleteNote = deleteNote;

            scope.note = {};
            scope.note.type = 0;

            activate();

            ////////

            function activate() {
                // Somehow calling autosize on page content load does not work
                // in the historylist.
                autosize($('textarea'));
                loadMore();
            }

            function loadMore() {
                if (!scope.object.$resolved) {
                    scope.object.$promise.then(function(obj) {
                        _fetchHistory(obj);
                    })
                } else {
                    _fetchHistory(scope.object);
                }
            }

            function reloadHistory() {
                page -= 1;
                loadMore();
            }

            function _fetchHistory(obj) {
                var history = [];
                var promises = [];
                page += 1;
                var neededLength = page * pageSize;

                // Check if we need to fetch notes
                if (noteTargets.indexOf(scope.target) != -1) {
                    var notePromise = NoteDetail.query({filterquery: 'content_type:' + scope.target + ' AND object_id:' + obj.id, size: neededLength }).$promise;
                    promises.push(notePromise);  // Add promise to list of all promises for later handling

                    notePromise.then(function(results) {
                        results.forEach(function(note) {
                            history.push(note);
                        });
                    });
                }

                // Check if we need to fetch cases
                if (caseTargets.indexOf(scope.target) != -1) {
                    var casePromise = CaseDetail.query({filterquery: scope.target + ':' + obj.id, size: neededLength}).$promise;
                    promises.push(casePromise);  // Add promise to list of all promises for later handling

                    casePromise.then(function(results) {
                        results.forEach(function(caseItem) {
                            history.push(caseItem);
                            NoteDetail.query({filterquery: 'content_type:case AND object_id:' + caseItem.id, size: 5})
                                .$promise.then(function(notes) {
                                    caseItem.notes = notes;
                                });
                        });
                    });
                }

                // Check if we need to fetch deals
                if (dealTargets.indexOf(scope.target) != -1) {
                    var dealPromise = DealDetail.query({filterquery: scope.target + ':' + obj.id, size: neededLength}).$promise;
                    promises.push(dealPromise);  // Add promise to list of all promises for later handling

                    dealPromise.then(function(results) {
                        results.forEach(function(deal) {
                            NoteDetail.query({
                                filterquery: 'content_type:deal AND object_id:' + deal.id,
                                size: 5
                            }).$promise.then(function (notes) {
                                    deal.notes = notes;
                                });
                            history.push(deal);
                        });
                    });
                }

                // Check if we need to fetch emails
                if (emailTargets.indexOf(scope.target) != -1) {
                    var tenantEmailAccountPromise = EmailAccount.query().$promise;
                    promises.push(tenantEmailAccountPromise); // Add tenant email query to promises list

                    var emailPromise;
                    if (scope.target == 'account') {
                        emailPromise = EmailDetail.query({account_related: obj.id, size: neededLength}).$promise;
                    } else {
                        emailPromise = EmailDetail.query({contact_related: obj.id, size: neededLength}).$promise;
                    }
                    promises.push(emailPromise);  // Add promise to list of all promises for later handling

                    $q.all([tenantEmailAccountPromise, emailPromise]).then(function(results) {
                        var tenantEmailAccountList = results[0];
                        var emailMessageList = results[1];

                        emailMessageList.forEach(function(email) {
                            tenantEmailAccountList.forEach(function (emailAddress) {
                                if (emailAddress.email_address === email.sender_email) {
                                    email.right = true;
                                }
                            });
                            history.push(email);
                        });
                    });
                }

                // Get all history types and add them to a common history
                $q.all(promises).then(function() {
                    var orderedHistoryList = [];

                    // Order our current historylist
                    $filter('orderBy')(history, 'date', true).forEach(function(item) {
                        // We have on of these items so we need to be able to filter on it
                        scope.history.types[item.historyType].visible = true;

                        // Push our item to our ordered list
                        orderedHistoryList.push(item);
                    });
                    if (!orderedHistoryList) {
                        // Make sure the max size of the list doesn't grow each click
                        page -= 1;

                        // Set the button text to inform the user what's happening
                        scope.history.showMoreText = 'No history (refresh)';
                    }
                    else if (orderedHistoryList.length <= neededLength) {
                        // Make sure the max size of the list doesn't grow each click
                        page -= 1;

                        // Set the button text to inform the user what's happening
                        scope.history.showMoreText = 'End reached (refresh)';
                    }

                    // Set the historylist to our new list
                    scope.history.list = orderedHistoryList.slice(0, neededLength);
                });
            }

            function addNote(note) {
                $http({
                    method: 'POST',
                    url: '/notes/create/',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    data: $.param({
                        content: note.content,
                        type: note.type,
                        content_type: scope.target,
                        object_id: scope.object.id
                    })
                }).success(function() {
                    $state.go($state.current, {}, {reload: true});
                });
            }

            function editNote(note) {
                var modalInstance = $modal.open({
                    templateUrl: 'utils/controllers/note_edit.html',
                    controller: 'EditNoteModalController',
                    size: 'lg',
                    resolve: {
                        note: function() {
                            return note;
                        }
                    }
                });

                modalInstance.result.then(function() {
                    $state.go($state.current, {}, {reload: true});
                });
            }

            function deleteNote(note) {
                if (confirm('Are you sure?')) {
                    Note.delete({
                        id:note.id
                    }, function() {  // On success
                        var index = scope.history.list.indexOf(note);
                        scope.history.list.splice(index, 1);
                    }, function(error) {  // On error
                        alert('something went wrong.')
                    });
                }
            }
        }
    }
}


})(angular);
(function(angular){
'use strict';
angular.module('app.utils.directives').directive('historyListItem', HistoryListItemDirective);

HistoryListItemDirective.$inject = ['$compile', '$http', '$templateCache'];
function HistoryListItemDirective($compile, $http, $templateCache) {
    return {
        restrict: 'E',
        scope: {
            item:'=',
            history:'='
        },
        link: function(scope, element, attrs) {
            var getTemplate = function(historyType) {
                var templateLoader,
                    baseUrl = 'utils/directives/history_list_',
                    templateMap = {
                        case: 'case.html',
                        deal: 'deal.html',
                        email: 'email.html',
                        note: 'note.html'
                    };

                var templateUrl = baseUrl + templateMap[historyType];
                templateLoader = $http.get(templateUrl, {cache: $templateCache});

                return templateLoader;
            };
            getTemplate(scope.item.historyType).success(function(html) {
                element.replaceWith($compile(html)(scope));
            }).then(function () {
                element.replaceWith($compile(element.html())(scope));
            });
        }
    };
}

})(angular);
})(angular);
//# sourceMappingURL=app.js.map