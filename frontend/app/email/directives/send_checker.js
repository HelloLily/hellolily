angular.module('app.email.directives').directive('sendChecker', sendCheckerDirective);

sendCheckerDirective.$inject = ['EmailAddress'];
function sendCheckerDirective(EmailAddress) {
    return {
        restrict: 'A',
        link: function(scope, element) {
            element.on('click', function(event) {
                var invalidAddresses;

                // Check recipients.
                var recipientsTo = $('#id_send_to_normal').val();
                var recipientsCc = $('#id_send_to_cc').val();
                var recipientsBcc = $('#id_send_to_bcc').val();
                var subject = angular.element('#id_subject').val();
                var allRecipients = [];

                if (!recipientsTo && !recipientsCc && !recipientsBcc) {
                    event.stopPropagation();
                    event.preventDefault();
                    bootbox.alert('I couldn\'t find a recipient, could you please fill in where I need to send this mail.');
                    return;
                }

                if (recipientsTo) allRecipients.push(recipientsTo);
                if (recipientsCc) allRecipients.push(recipientsCc);
                if (recipientsBcc) allRecipients.push(recipientsBcc);

                if (allRecipients) {
                    allRecipients = allRecipients.join(',');

                    invalidAddresses = EmailAddress.checkValidityOfEmailList(allRecipients);

                    if (invalidAddresses && invalidAddresses.length) {
                        event.stopPropagation();
                        event.preventDefault();
                        invalidAddresses = invalidAddresses.join('<br />');
                        bootbox.dialog({
                            message: 'There seem to be some invalid email addresses in your message?<br />' +
                            invalidAddresses,
                            title: 'Invalid email addresses',
                            buttons: {
                                danger: {
                                    label: 'Oops, I\'ll fix it',
                                    className: 'btn-danger',
                                },
                                success: {
                                    label: 'No problem, send it anyway',
                                    className: (subject !== '') ? 'btn-success' : 'hidden',
                                    callback: function() {
                                        HLInbox.submitForm('submit-send', element.closest('form')[0]);
                                    },
                                },
                            },
                        });
                        return;
                    }
                }

                // Check subject.
                if (subject === '') {
                    event.stopPropagation();
                    event.preventDefault();
                    bootbox.dialog({
                        message: 'Are you sure you want to send this email without a subject?',
                        title: 'No subject',
                        buttons: {
                            danger: {
                                label: 'Oops, I\'ll fix it',
                                className: 'btn-danger',
                            },
                            success: {
                                label: 'No problem, send it anyway',
                                className: 'btn-success',
                                callback: function() {
                                    HLInbox.submitForm('submit-send', element.closest('form')[0]);
                                },
                            },
                        },
                    });

                    return;
                }
            });
        },
    };
}

