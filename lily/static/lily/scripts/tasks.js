(function ($, window, document, undefined) {
    window.HLTasks = {
        config: {
            placeholderUrl: '/taskmonitor/task/status/000/',
            sendMessageSuccess: 'Your message has been sent!',
            sendMessageSuccessTitle: 'Success!',
            sendMessageError: 'There was an error while sending your mail, please try again!',
            sendMessageErrorTitle: 'Oops!'
        },

        init: function (config) {
            // Setup config
            if (typeof (config === 'object')) {
                $.extend(this.config, config);
            }

            this.setupListeners();
        },

        setupListeners: function() {
            $('document')
                .on('taskmonitor_send_message', function (event) {
                    // Format phonenumbers for every phone input field
                    if (event.task_result) {
                        toastr.success(this.config.sendMessageSuccess);
                    }
                    else {
                        toastr.error(this.config.sendMessageError);
                    }
                });
        },

        getTaskUri: function (taskId) {
            return this.config.placeholderUrl.replace('000', taskId);
        },

        getTaskResponse: function (taskId) {
            var self = this;
            var timeout = setTimeout(function () {
                var url = self.getTaskUri(taskId);

                $.getJSON(url)
                    .done(function (response) {
                        if (response.task_status !== 'STARTED') {
                            var event_name = 'taskmonitor_' + response.task_name;

                            $(document).trigger({
                                type: event_name,
                                task_id: taskId,
                                task_result: response.task_result
                            });

                            clearTimeout(timeout);
                        }
                    });
            }, 2000);
        }
    };
})(jQuery, window, document);
