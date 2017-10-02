angular.module('app.services').factory('HLMessages', HLMessages);

HLMessages.$inject = [];
function HLMessages() {
    var mod = 'CTRL';
    if (navigator.userAgent.indexOf('Mac OS X') !== -1) {
        mod = '⌘';
    }

    return {
        contact: {
            accountInfoTooltip: 'I\'ve loaded the selected account\'s data for you. Now you don\'t have to enter duplicate data!',
            accountListInfoTooltip: 'This is the data of the account(s) the contact works for',
            contactInfoTooltip: 'This is the current contact\'s data',
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
                datepicker: 'Or manually select a date:',
            },
            dashboard: {
                title: 'Widget settings',
            },
            deals: {
                title: 'Why lost?',
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
            featureUnavailable: 'This feature is unavailable for your current plan. Click here to go to the billing page.',
        },
    };
}
