angular.module('app.services').factory('HLMessages', HLMessages);

HLMessages.$inject = [];
function HLMessages() {
    let mod = 'CTRL';

    if (navigator.userAgent.indexOf('Mac OS X') !== -1) {
        mod = '⌘';
    }

    let featureUnavailable;
    let limitReached;
    let sharingUnavailable;

    if (currentUser.isAdmin) {
        featureUnavailable = 'This feature is unavailable for your current plan. Click here to go to the billing page.';
        limitReached = 'You\'ve reached the email account limit of your Personal plan. Please <a href="/#/preferences/admin/billing">upgrade</a> it to enable more email accounts.';
        sharingUnavailable = 'Email accounts can\'t be shared while on the Personal plan. Please <a href="/#/preferences/admin/billing">upgrade</a> it to enable inbox sharing.';
    } else {
        featureUnavailable = `This feature is unavailable for your current plan. Ask ${currentUser.tenant.accountAdmin} to upgrade your plan.`;
        limitReached = `You've reached the email account limit of your Personal plan. Ask ${currentUser.tenant.accountAdmin} to upgrade your plan.`;
        sharingUnavailable = `Email accounts can't be shared while on the Personal plan. Ask ${currentUser.tenant.accountAdmin} to upgrade your plan.`;
    }

    return {
        general: {
            featureUnavailable,
            featureUnavailableInline: 'This feature is unavailable for your current plan. <br />Please <a href="/#/preferences/admin/billing">upgrade</a> to use this feature.',
        },
        pages: {
            notFoundTitle: 'Not found',
            serverErrorTitle: 'Error',
            accounts: {
                addContactToExisting: 'Add as a contact to an existing account instead?',
                accountExists: 'It looks like this account already exists',
                emptyStateTitle: 'Progressional overview of what’s going on',
                emptyStateOne: 'Accounts are a collection of contacts within the same organization, company or group.',
                emptyStateTwo: 'You can easily see who you’ve been talking to and when.',
                emptyStateThree: 'See the full communication history and gain insights about them, if you add them as an',
            },
            contacts: {
                contactExists: 'It looks like this contact already exists',
                accountInfoTooltip: 'I\'ve loaded the selected account\'s data for you. Now you don\'t have to enter duplicate data!',
                accountListInfoTooltip: 'This is the data of the account(s) the contact works for',
                contactInfoTooltip: 'This is the current contact\'s data',
                emptyStateTitle: 'Everyone that matters to you',
                emptyStateOne: 'Contacts are the lifeline for your communication history.',
                emptyStateTwo: 'All emails, logged phone calls and notes added by you or your colleagues will be linked to them.',
                emptyStateThree: 'Never lose track of anyone or anything, and add them as a ',
                contactActiveAtIntro: 'For each account you can toggle if <strong>%(name)s</strong> is still active there.',
                contactActiveAtText: 'This won\'t affect the visablilty of past communication.',
            },
            cases: {
                openCase: 'There\'s another open case',
                openCases: 'There are other open cases',
                emptyStateTitle: 'Progressional overview of what’s going on',
                emptyStateOne: 'Here you’ll find what needs to be done. Keep track of your tasks.',
                emptyStateTwo: 'Start right now and add a',
            },
            deals: {
                openDeal: 'There\'s another open deal',
                openDeals: 'There are other open deals',
                emptyStateTitle: 'Close that deal',
                emptyStateOne: 'Track the status of your deals with this extensive overview.',
                emptyStateTwo: 'You can see what’s expired and what needs to be done in the nearby future.',
                emptyStateThree: 'Add your first real deal, to find out',
            },
            email: {
                importingEmail: 'Importing your email',
                failedLoading: 'Unable to load email',
                noVariables: 'No template variables yet. You should create one!',
                noPublicVariables: 'No public template variables yet.',
                firstSetupHeader: 'Connect your Gmail account and Lily will show her true power.',
                firstSetupText: 'Share your email conversations with colleagues, so your organization will be able to respond based on a complete history of communication.',
                noFolders: 'No folders yet. You should create one!',
                noTemplates: 'No templates yet. You should create one!',
                accountShare: 'Give specific colleagues additional permissions to your email',
                accountForm: {
                    loadAllMail: 'Load all mail into Lily?',
                    loadAllMailYes: 'Yes, load all email into Lily',
                    loadAllMailNo: 'No, only load email received from now on',
                    inboxTitle: 'This inbox is a',
                    publicInboxInfo: 'Used by multiple people in the company, ergo info@ or support@',
                    publicInboxExampleText: 'Example for your convenience',
                    readOnlyInboxInfo: 'Hi! I just wanted to show an example of what your colleagues can read.',
                    readOnlyInboxInfoSignature: 'Love Lily!',
                    advancedInfo: 'Give specific colleagues additional permissions to your email',
                },
                accountList: {
                    limitReached,
                    sharingUnavailable,
                },
            },
            errors: {
                notFoundTitle: '404 - page not found',
                notFound: 'I searched the universe to find this page, but it does not exist.',
                serverErrorTitle: '500 - internal server error',
                serverError: 'Darn, my space rocket won\'t launch due to technical issues.',
                serverErrorSub: 'I will get that fixed. Please be patient in the meantime.',
            },
            generic: {
                unknownUser: 'An unknown entity',
                widgetItemSuggest: 'Check it out',
                doesNotExist: 'Sorry, does not exist.',
            },
            integrations: {
                overview: 'This page contains other applications which can be integrated into Lily.',
                moneybirdOverview: 'This page shows actions you can do with Moneybird.',
                moneybirdContactImportIntro: 'This page allows you to import your Moneybird contacts into Lily.',
                moneybirdContactImportInfo: 'Checking this box means changes to your Lily contacts will be submitted to Moneybird too. This also means contacts created and updated in Lily will be synced with Moneybird.',
                moneybirdContactImportCheckbox: 'Sync Lily contacts with Moneybird',
                moneybirdContactImportNote: 'Automatic sync from Moneybird to Lily isn\'t supported (yet).<br /> However, you can press this button whenever you need to synchronize your Moneybird contacts again.',
                moneybirdContactImportNoCredentials: 'It seems like you haven\'t set your <a ui-sref="base.preferences.admin.integrations.moneybird.auth">Moneybird credentials</a> yet.',
                moneybirdContactImportNoCredentialsSub: 'Please setup the Moneybird integration before continuing.',
                pandaDocOverview: 'This page shows actions you can do with PandaDoc.',
                pandaDocWebhooksIntro: 'Set up webhooks to update deals based on received events.',
                pandaDocWebhooksIntroSub: 'Enter the following url in PandaDoc to start receiving document updates.',
                pandaDocWebhooksInstructionsOne: 'What status should the deal be set to',
                pandaDocWebhooksInstructionsTwo: 'What step should the deal be set to',
                pandaDocWebhooksInstructionsThree: 'Amount of days to add to the next step date',
                pandaDocWebhooksInstructionsFour: 'Sets the date to the date the event was triggered (can\'t be used together with \'Extra days\')',
                pandaDocWebhooksInstructionsFive: 'Should a note be added when this event occurs',

                slackOverview: 'Use the button below to install the Lily Slack app. <br /> This app will read links related to Lily (e.g. when you link a case) and provide you with a preview in Slack.',
            },
            preferences: {
                passwordMismatch: 'Your passwords don\'t match.',
                webhookIntro: 'You can enter a URL here to call whenever a create (POST) or update (PUT/PATCH) event is executed (e.g. an account being created or updated).',
                notificationsDisabledTitle: 'Browser notifications have been blocked',
                notificationsDisabled: 'You will not receive call notifications, but your calls will still be visible in activity streams.',
                apiToken: {
                    noToken: 'No token generated for you',
                    noTokenInfo: 'You need to generate a token before you can use it in your API calls',
                    usageInfo: 'You can use your token with an authorization header',
                    usageInfoAlt: 'Or you can use your token with an url parameter',
                },
            },
            import: {
                accountIntro: 'List accounts all at once by importing a .csv file containing account information.',
                contactIntro: 'List contacts all at once by importing a .csv file containing account information.',
                instructionsOne: 'Only .CSV files are eligible',
                instructionsTwo: 'The file should at least contain a column with the header',
                instructionsThree: 'Optional headers are',
                instructionsFourAccount: 'Information in any additional columns will be added to the description of an account',
                instructionsFourContact: 'Information in any additional columns will be added to the description of a contact',
                instructionsFive: 'Please note that headers are case sensitive',
            },
            settings: {
                header: 'Additional features',
                timeLogging: 'Enable this feature so users can log hours on cases and deals.',
                billingDefault: 'Sets the default for the \'Billable\' value for logged hours.',
            },
            security: {
                backupTokenIntro: 'These are your current backup tokens, they will be regenerated after you\'ve used them all.',
                noTwoFactorEnabled: 'you have not enabled two factor authentication yet.',
                backupPhonesInfo: 'If your primary method is not available, we are able to send backup tokens to your phone number(s).',
                backupPhonesInfoTooltip: 'Let me see my phone numbers!',
                noBackupPhones: 'You currently have no backup phone number(s) available. It is highly recommended that you add one!',
                noBackupPhonesTooltip: 'Add a new backup phone number',
                backupTokenInfo: 'If you don\'t have any device with you, you can access your account using backup tokens.',
                backupTokenInfoTooltip: 'Let me see my tokens!',
            },
            other: {
                inviteUsersIntro: 'Adding users adds extra costs to your team\'s subscription. Ask <strong>{{ vm.accountAdmin.full_name }}</strong> if you’re not sure about this.',
            },
        },
        notifications: {
            dataProvider: {
                info: 'Running around the world to fetch info',
                infoTitle: 'Here we go',
                success: 'Got it!',
                error: 'I couldn\'t find any data',
                errorTitle: 'Sorry',
            },
            successTitle: 'Done',
            modelSaved: 'The %(model)s has been saved!',
            modelUpdated: 'The %(model)s has been updated!',
            modelDeleted: 'The %(model)s has been deleted!',
            error: 'Uh oh, there seems to be a problem',
            errorInline: 'Something went wrong while saving the field, please try again.',
            errorTitle: 'Oops',
            loggedOut: 'You\'ve been logged out, please reload the page.',
            failedLoad: 'Couldn\'t load notifications',
            noCalls: 'No calls for you right now',
            noCallsTitle: 'No calls',
            emailTemplateLoadError: 'I couldn\'t load the template because your email account doesn\'t seem to be set. Please check your email account and try again',
            defaultTemplateLoadError: 'Sorry, I couldn\'t load your default email template. You could try reloading the page',
            subscriptionUpdated: 'Your subscription has been changed',
            subscriptionError: 'Your subscription couldn\'t be changed. Please try again',
            accountImportSuccess: 'I\'ve imported your accounts!',
            contactImportSuccess: 'I\'ve imported your contacts!',
            moneybirdImportStart: 'The import will continue in the background. Feel free to continue using Lily',
            moneybirdImportStartTitle: 'Import started',
            invitationSent: 'The invitations were sent successfully',
            userListLoadError: 'Could not load the user list, please try again later.',
            profileUpdated: 'Your profile has been updated',
            timeLogged: 'Your hours have been logged',
            noteCreated: 'I\'ve created the note for you!',
            emptyNoteError: 'You can\'t create an empty note!',
            twoFactorPhoneRemoved: 'The phone number was successfully removed',
            twoFactorNewTokens: 'You now have a new set of backup tokens!',
            sessionEnded: 'The session was successfully ended',
            sessionEndedTitle: 'Session ended!',
            passwordMismatch: 'Your passwords don\'t match. Please fix and try again.',
            passwordMismatchTitle: 'Attention!',
            userAccountUpdated: 'I\'ve updated your account!',
            apiTokenCreated: 'I\'ve created a new one',
            apiTokenCreatedTitle: 'Token generated',
            apiTokenDeleted: 'And it\'s gone!',
            apiTokenDeletedTitle: 'Token deleted',
            unauthorizedEmailAccount: 'Oops, something went wrong with one of your email accounts, could you help me fix it?',
        },
        alerts: {
            accountForm: {
                title: 'Website already exists',
                body: 'This website has already been added to an existing account: <br />' +
                '<strong>%(account)s</strong><br />' +
                'Are you sure you want to use:<br />' +
                '%(website)s',
                cancelButtonText: 'No, clear the field',
            },
            delete: {
                confirmTitle: 'Are you sure?',
                confirmText: 'You are about to delete <strong>%(name)s</strong>.<br />You won\'t be able to revert this!',
                confirmButtonText: 'Yes, delete it!',
                successTitle: 'Deleted',
                successText: 'The %(model)s <strong>%(name)s</strong> has been deleted.',
                errorTitle: 'Error',
                errorText: 'There was an error processing your request.<br />Please try again.',
            },
            assignTo: {
                title: 'Assign this %(type)s',
                questionText: 'Assign this %(type)s to yourself?',
            },
            deactivateUser: {
                confirmText: 'Are you sure you want to deactivate <strong>%(name)s</strong>',
                confirmButtonText: 'Yes, deactivate',
                successTitle: 'Deactivated!',
                successText: '<strong>%(name)s</strong> has been deactivated.',
            },
            resendUserInvite: {
                title: 'Resend invite',
                confirmText: 'Are you sure you want to resend the invite to <strong>%(email)s</strong>',
                success: 'The invitation was resent successfully',
                confirmButtonText: 'Yes, resend invite',
            },
            removeUserInvite: {
                confirmText: 'Are you sure you want to delete the invite for <strong>%(name)s</strong>',
            },
            postpone: {
                dealTitle: 'Change next step date',
                caseTitle: 'Change expiry date',
                deal: 'Wrong day to solve it?<br />Set to today or postpone it.',
                case: 'Not the right day to act upon it?<br />Set to today or postpone it.',
                subText: '<strong>Note: </strong> Weekends are automatically skipped',
                datepicker: 'Or manually select a date:',
                confirmButtonText: 'Postpone',
            },
            timeLog: {
                modalTitle: 'Time logging',
                confirmButtonText: 'Log time',
                invalidTime: 'Invalid value provided',
            },
            dashboard: {
                title: 'Widget settings',
            },
            cases: {
                noSelectionTitle: 'No account or contact',
                noSelectionText: 'Please select an account or contact the case belongs to',
                confirmButtonText: 'Let me fix that for you',
                noAssigneeTitle: 'No assignee set',
                noAssigneeText: 'Please select a colleague or team to assign the case to',
            },
            deals: {
                title: 'Why lost?',
                noSelectionTitle: 'No account or contact',
                noSelectionText: 'Please select an account or contact the deal belongs to',
                confirmButtonText: 'Let me fix that for you',
                whyLostReason: 'Please select a reason why this deal has been lost.',
            },
            email: {
                sendCheckerTitle: 'No recipient',
                sendCheckerText: 'I couldn\'t find a recipient, could you please fill in where I need to send this mail.',
                overwriteTemplateConfirm: 'Selecting a different template will reload the template. This will put your typed text at the bottom of the email. Do you want to load the template anyway?',
                reloadTemplateConfirm: 'Do you want to reload the template? This will load the template variables, but will put your text at the bottom of the email.',
            },
            notificationPermission: {
                title: 'Heads up!',
                text: 'For our call integration, we need your browsers permission to send you notifications. Please allow these notifications to make complete use of our call integration.',
            },
            preferences: {
                userAssignTitle: 'Assign %(user)s to teams',
                shareAccountTitle: 'Share your email',
                subscription: {
                    cancelTitle: 'Are you sure?',
                    cancelText: 'You are about to cancel your subscription. This will revert your account back to the free plan after the next billing date. Are you sure you want to continue?',
                    trialStartTitle: 'Start trial?',
                    trialStartText: 'Are you sure you want to start your 30 day trial of the professional plan?',
                    trialConfirm: 'Start trial',
                },
                confirmButtonText: 'Yes, cancel!',
                twoFactorAuth: {
                    disable: {
                        confirmText: 'You are about to disable two-factor authentication. This compromises your account security, are you sure?',
                        confirmButtonText: 'Yes, disable',
                        successTitle: 'Disabled!',
                        successText: 'Two factor auth was successfully disabled.',
                    },
                    removeBackupPhoneNumber: {
                        title: 'Are you sure?',
                        html: 'This means you will no longer be able to login using this phone number.',
                        confirmButtonText: 'Yes, remove it',
                        error: {
                            title: 'Error',
                            html: 'There was an error processing your request.<br />Please try again.',
                        },
                    },
                    endSession: {
                        title: 'Are you sure?',
                        html: 'This means that you will be logged out from this device.',
                        confirmButtonText: 'Yes, end this session',
                        error: {
                            title: 'Error',
                            html: 'There was an error processing your request.<br />Please try again.',
                        },
                    },
                    backup: {
                        confirmButtonText: 'Regenerate',
                    },
                },
                disableTwoFactorAuth: {
                    confirmText: 'You are about to disable two-factor authentication. This compromises your account security, are you sure?',
                    confirmButtonText: 'Yes, disable',
                    successTitle: 'Disabled!',
                    successText: 'Two factor auth was successfully disabled.',
                },
            },
            general: {
                errorTitle: 'Error',
                errorText: 'There was an error processing your request.<br />Please try again.',
            },
            widgetSettings: 'Check/uncheck a widget to toggle the visibility of the widget.',
        },
        activityStream: {
            emailMetadataMessage: 'The content of this email is not visible to you because the owner has chosen not to share the full message',
        },
        tooltips: {
            modEnter: {
                title: mod + '+Enter',
            },
            newlyAssignedCase: 'Add it to \'My cases\'',
            newlyAssignedDeal: 'Add it to \'My deals\'',
            emailAccountConnectionWarning: 'To solve email issues, please click to add this email account again',
            emailAccountPublicTooltip: 'All colleagues in %(company)s',
            limitReached: 'You\'ve reached the limit of your Personal plan. Please upgrade it to add more %(model)s.',
            filterArchived: 'This item has been archived, but can still be filtered on',
            contactIcon: {
                loading: 'Loading status, hang on!',
                needsEverything: 'New account, unknown contact. Do the add thing!',
                needsContact: 'Hey, a new contact for the account! Add it for optimal Lily magic.',
                needsAccount: 'Hey, a contact without an account! Add it for optimal Lily magic.',
                complete: 'All done. Do a happy dance.',
            },
        },
    };
}
