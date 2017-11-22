angular.module('app.email').config(emailConfig);

emailConfig.$inject = ['$stateProvider'];
function emailConfig($stateProvider) {
    const emailComposeView = {
        '@base.email': {
            templateUrl: '/messaging/email/compose/',
            controller: EmailComposeController,
            controllerAs: 'vm',
        },
    };

    $stateProvider.state('base.email.compose', {
        url: '/compose',
        views: emailComposeView,
    });
    $stateProvider.state('base.email.composeEmail', {
        url: '/compose/{email}',
        views: emailComposeView,
    });
    $stateProvider.state('base.email.composeEmailDocument', {
        url: '/compose/{email}/{documentId}',
        views: emailComposeView,
    });
    $stateProvider.state('base.email.composeEmailTemplate', {
        url: '/compose/{email}/{template}',
        views: emailComposeView,
    });
    $stateProvider.state('base.email.draft', {
        url: '/draft/{id:[0-9]{1,}}',
        params: {
            messageType: 'draft',
        },
        views: {
            '@base.email': {
                templateUrl: (elem, attr) => '/messaging/email/draft/' + elem.id + '/',
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
                templateUrl: (elem, attr) => '/messaging/email/reply/' + elem.id + '/',
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
                templateUrl: (elem, attr) => '/messaging/email/reply/' + elem.id + '/',
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
                templateUrl: (elem, attr) => '/messaging/email/replyall/' + elem.id + '/',
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
                templateUrl: (elem, attr) => '/messaging/email/forward/' + elem.id + '/',
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
    const vm = this;

    Settings.page.setAllTitles('custom', 'Compose email');

    vm.discard = discard;

    activate();

    //////////

    function activate() {
        // Remove cache so new compose will always hit the server.
        $templateCache.remove('/messaging/email/compose/');

        if ($stateParams.messageType === 'reply') {
            // If it's a reply, load the email message first.
            EmailMessage.get({id: $stateParams.id}).$promise.then(emailMessage => {
                _initEmailCompose(emailMessage);
            });
        } else {
            // Otherwise just initialize the email compose.
            _initEmailCompose();
        }
    }

    function _initEmailCompose(emailMessage) {
        const promises = [];

        let email = $stateParams.email;
        let recipient = null;
        let contactPromise;
        let filterquery;

        if (emailMessage) {
            // It's a reply, so try to load a contact with the given email address.
            filterquery = 'email_addresses.email_address:"' + emailMessage.sender.email_address + '"';
        } else if (email) {
            // Otherwise try to load a contact with the email in the url.
            filterquery = 'email_addresses.email_address:"' + email + '"';
        }

        if (filterquery) {
            filterquery += ' AND ';
        }

        filterquery += 'email_addresses.is_active:true';

        if (filterquery) {
            contactPromise = Contact.search({filterquery}).$promise;
            promises.push(contactPromise);
        }

        const emailTemplatePromise = EmailTemplate.query().$promise;
        promises.push(emailTemplatePromise);

        // TODO: LILY-XXX: Check if this can be cleaned up
        // Continue once all promises are done.
        $q.all(promises).then(results => {
            let templates;

            // This part should only be executed if we've loaded a contact.
            if (contactPromise) {
                const contact = results[0].objects[0];
                templates = results[1].results;

                if (emailMessage && !email) {
                    if (emailMessage.reply_to) {
                        email = emailMessage.reply_to;
                    } else {
                        email = emailMessage.sender.email_address;
                    }
                }

                if (contact) {
                    // The text which is actually used in the application/select2.
                    const usedText = '"' + contact.full_name + '" <' + email + '>';
                    // The text shown in the recipient input.
                    const displayedText = contact.full_name + ' <' + email + '>';

                    recipient = {
                        id: usedText,
                        text: displayedText,
                        object_id: contact.id,
                    };
                } else if (email) {
                    recipient = {
                        id: email,
                        text: email,
                        object_id: null,
                    };
                }
            } else {
                templates = results[0];
            }

            const template = $stateParams.template;
            // Determine whether the default template should be loaded or not.
            const loadDefaultTemplate = template === undefined;

            // Set message type to given message type if available, otherwise set to message type 'new'.
            const messageType = $stateParams.messageType ? $stateParams.messageType : 'new';

            HLInbox.init();

            if (SelectedEmailAccount.currentAccountId) {
                angular.element(HLInbox.config.emailAccountInput).select2('val', SelectedEmailAccount.currentAccountId);
            }

            HLInbox.initEmailCompose({
                messageType,
                loadDefaultTemplate,
                recipient,
                template,
                templateList: templates,
                recipientEmail: $stateParams.email,
                documentId: $stateParams.documentId,
                defaultEmailTemplateUrl: '/messaging/email/templates/get-default/',
                getTemplateUrl: '/messaging/email/templates/detail/',
            });

            HLInbox.setSuccesURL($scope.previousState);
            HLInbox.setCurrentInbox(Settings.email.previousInbox.params.labelId);
        });
    }

    function discard() {
        if ($stateParams.messageType === 'draft') {
            EmailMessage.trash({id: $stateParams.id}).$promise.then(() => {
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

    // Listen to Angular broadcast function on scope destroy.
    $scope.$on('$destroy', () => {
        // Properly destroy the rich text editor to prevent memory leaks.
        HLInbox.destroyEditor();
    });
}
