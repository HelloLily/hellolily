angular.module('app.email').config(emailConfig);

emailConfig.$inject = ['$stateProvider'];
function emailConfig($stateProvider) {
    // TODO: LILY-XXX: Clean up compose states and make email/template optional params
    $stateProvider.state('base.email.compose', {
        url: '/compose',
        views: {
            '@base.email': {
                templateUrl: '/messaging/email/compose/',
                controller: EmailComposeController,
                controllerAs: 'vm',
            },
        },
    });
    $stateProvider.state('base.email.composeEmail', {
        url: '/compose/{email}/{contactId}',
        views: {
            '@base.email': {
                templateUrl: '/messaging/email/compose/',
                controller: EmailComposeController,
                controllerAs: 'vm',
            },
        },
    });
    $stateProvider.state('base.email.composeEmailTemplate', {
        url: '/compose/{email}/{template}',
        views: {
            '@base.email': {
                templateUrl: '/messaging/email/compose/',
                controller: EmailComposeController,
                controllerAs: 'vm',
            },
        },
    });
    $stateProvider.state('base.email.draft', {
        url: '/draft/{id:[0-9]{1,}}',
        params: {
            messageType: 'draft',
        },
        views: {
            '@base.email': {
                templateUrl: function(elem, attr) {
                    return '/messaging/email/draft/' + elem.id + '/';
                },
                controller: EmailComposeController,
                controllerAs: 'vm',
            },
        },
    });
    $stateProvider.state('base.email.reply', {
        url: '/reply/{id:[0-9]{1,}}',
        params: {
            messageType: 'reply',
        },
        views: {
            '@base.email': {
                templateUrl: function(elem, attr) {
                    return '/messaging/email/reply/' + elem.id + '/';
                },
                controller: EmailComposeController,
                controllerAs: 'vm',
            },
        },
    });
    $stateProvider.state('base.email.replyOtherEmail', {
        url: '/reply/{id:[0-9]{1,}}/{email}',
        params: {
            messageType: 'reply',
        },
        views: {
            '@base.email': {
                templateUrl: function(elem, attr) {
                    return '/messaging/email/reply/' + elem.id + '/';
                },
                controller: EmailComposeController,
                controllerAs: 'vm',
            },
        },
    });
    $stateProvider.state('base.email.replyAll', {
        // TODO: This should probably be redone so the url is nicer.
        // Maybe we can save the action in the scope?
        url: '/replyall/{id:[0-9]{1,}}',
        params: {
            messageType: 'reply-all',
        },
        views: {
            '@base.email': {
                templateUrl: function(elem, attr) {
                    return '/messaging/email/replyall/' + elem.id + '/';
                },
                controller: EmailComposeController,
                controllerAs: 'vm',
            },
        },
    });
    $stateProvider.state('base.email.forward', {
        url: '/forward/{id:[0-9]{1,}}',
        params: {
            messageType: 'forward',
        },
        views: {
            '@base.email': {
                templateUrl: function(elem, attr) {
                    return '/messaging/email/forward/' + elem.id + '/';
                },
                controller: EmailComposeController,
                controllerAs: 'vm',
            },
        },
    });
}

angular.module('app.email').controller('EmailComposeController', EmailComposeController);

EmailComposeController.$inject = ['$scope', '$state', '$stateParams', '$templateCache', '$q', 'Settings', 'Contact',
    'EmailMessage', 'EmailTemplate', 'SelectedEmailAccount'];
function EmailComposeController($scope, $state, $stateParams, $templateCache, $q, Settings, Contact, EmailMessage,
                                EmailTemplate, SelectedEmailAccount) {
    var vm = this;

    Settings.page.setAllTitles('custom', 'Compose email');

    vm.discard = discard;

    activate();

    //////////

    function activate() {
        // Remove cache so new compose will always hit the server.
        $templateCache.remove('/messaging/email/compose/');

        if ($stateParams.messageType === 'reply') {
            // If it's a reply, load the email message first.
            EmailMessage.get({id: $stateParams.id}).$promise.then(function(emailMessage) {
                _initEmailCompose(emailMessage);
            });
        } else {
            // Otherwise just initialize the email compose.
            _initEmailCompose();
        }
    }

    function _initEmailCompose(emailMessage) {
        var email = $stateParams.email;
        var emailTemplatePromise;
        var promises = [];
        var recipient = null;
        var contactPromise;
        var template;
        var loadDefaultTemplate;
        var messageType;
        var filterquery;

        if (emailMessage) {
            // It's a reply, so try to load a contact with the given email address.
            filterquery = 'email_addresses.email_address:"' + emailMessage.sender.email_address + '"';
        } else if (email) {
            // Otherwise try to load a contact with the email in the url.
            filterquery = 'email_addresses.email_address:"' + email + '"';
        }

        if (filterquery) {
            contactPromise = Contact.search({filterquery: filterquery}).$promise;
            promises.push(contactPromise);
        }

        emailTemplatePromise = EmailTemplate.query().$promise;
        promises.push(emailTemplatePromise);

        // TODO: LILY-XXX: Check if this can be cleaned up
        // Continue once all promises are done.
        $q.all(promises).then(function(results) {
            var templates;
            var contact;
            var usedText;
            var displayedText;

            // This part should only be executed if we've loaded a contact.
            if (contactPromise) {
                contact = results[0].objects[0];
                templates = results[1].results;

                if (emailMessage && !email) {
                    email = emailMessage.sender.email_address;
                }

                if (contact) {
                    // The text which is actually used in the application/select2.
                    usedText = '"' + contact.full_name + '" <' + email + '>';
                    // The text shown in the recipient input.
                    displayedText = contact.full_name + ' <' + email + '>';

                    recipient = {
                        id: usedText,
                        text: displayedText,
                        object_id: contact.id,
                    };
                } else {
                    recipient = {
                        id: email,
                        text: email,
                        object_id: null,
                    };
                }
            } else {
                templates = results[0];
            }

            template = $stateParams.template;
            // Determine whether the default template should be loaded or not.
            loadDefaultTemplate = template === undefined;

            // Set message type to given message type if available, otherwise set to message type 'new'.
            messageType = $stateParams.messageType ? $stateParams.messageType : 'new';

            HLInbox.init();
            HLInbox.initEmailCompose({
                templateList: templates,
                defaultEmailTemplateUrl: '/messaging/email/templates/get-default/',
                getTemplateUrl: '/messaging/email/templates/detail/',
                messageType: messageType,
                loadDefaultTemplate: loadDefaultTemplate,
                recipient: recipient,
                template: template,
            });
            HLInbox.setSuccesURL($scope.previousState);
            if (SelectedEmailAccount.currentAccountId) {
                angular.element(HLInbox.config.emailAccountInput).select2('val', SelectedEmailAccount.currentAccountId);
            }
        });
    }

    function discard() {
        if ($stateParams.messageType === 'draft') {
            EmailMessage.trash({id: $stateParams.id}).$promise.then(function() {
                if (Settings.email.previousInbox) {
                    $state.transitionTo(Settings.email.previousInbox.state, Settings.email.previousInbox.params, false);
                } else {
                    $state.go('base.email.list', {labelId: 'INBOX'});
                }
            });
        } else {
            if (Settings.email.previousInbox) {
                $state.transitionTo(Settings.email.previousInbox.state, Settings.email.previousInbox.params, false);
            } else {
                $state.go('base.email.list', {labelId: 'INBOX'});
            }
        }
    }
}
