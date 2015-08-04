angular.module('app.email.directives').directive('sendChecker', sendCheckerDirective);

sendCheckerDirective.$inject = ['EmailAddress'];
function sendCheckerDirective (EmailAddress) {
    return {
        restrict: 'A',
        link: function (scope, element) {
            element.on('click', function (event) {
                // check recipients
                var recipients_to = $('#id_send_to_normal').val();
                var recipients_cc = $('#id_send_to_cc').val();
                var recipients_bcc = $('#id_send_to_bcc').val();
                var subject = angular.element('#id_subject').val();
                var all_recipients = [];

                if (!recipients_to && !recipients_cc && !recipients_bcc) {
                    event.stopPropagation();
                    event.preventDefault();
                    bootbox.alert('I couldn\'t find a recipient, could you please fill in where I need to send this mail.');
                    return;
                }

                if (recipients_to) all_recipients.push(recipients_to);
                if (recipients_cc) all_recipients.push(recipients_cc);
                if (recipients_bcc) all_recipients.push(recipients_bcc);

                if(all_recipients) {
                    all_recipients = all_recipients.join(',');

                    var invalid_addresses = EmailAddress.checkValidityOfEmailList(all_recipients);

                    if(invalid_addresses && invalid_addresses.length){
                        event.stopPropagation();
                        event.preventDefault();
                        invalid_addresses = invalid_addresses.join("<br />");
                        bootbox.dialog({
                            message: 'There seem to be some invalid email addresses in your message?<br />' +
                                        invalid_addresses,
                            title: 'Invalid email addresses',
                            buttons: {
                                danger: {
                                    label: 'Oops, I\'ll fix it',
                                    className: 'btn-danger'
                                },
                                success: {
                                    label: 'No problem, send it anyway',
                                    className: (subject != "") ? 'btn-success' : 'hidden',
                                    callback: function() {
                                        HLInbox.submitForm('submit-send', element.closest('form')[0]);
                                    }
                                }
                            }
                        });
                        return;
                    }
                }

                // check subject
                if (subject == '') {
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

                    return;
                }
            });
        }
    }
}

