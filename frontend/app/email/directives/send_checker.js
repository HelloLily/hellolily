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
                                    angular.element('#id_subject').closest('form').submit();
                                }
                            }
                        }
                    });
                }
            });
        }
    }
}

