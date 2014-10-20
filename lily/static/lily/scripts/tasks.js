(function ($, window, document, undefined) {
    window.HLTasks = {
        config: {
            placeholderUrl: '/taskmonitor/task/status/000/',
            sendMessageSuccess: {message: 'Your message has been sent!', title: 'Success!'},
            sendMessageError: {message: 'There was an error while sending your mail, please try again!', title: 'Oops!'}
        },

        init: function (config) {
            // Setup config
            if (typeof (config === 'object')) {
                $.extend(this.config, config);
            }

            this.initListeners();
        },

        initListeners: function() {
            var cf = this.config;

            $(document)
                .on('taskmonitor_send_message', function (event) {
                    if (event.task_result) {
                        toastr.success(cf.sendMessageSuccess.message, cf.sendMessageSuccess.title);
                    }
                    else {
                        toastr.error(cf.sendMessageError.message, cf.sendMessageError.title);
                    }
                });
        },

        getTaskUri: function (taskId) {
            return this.config.placeholderUrl.replace('000', taskId);
        },

        getTaskResponse: function (taskId) {
            var self = this;
            var attempts = 0;
            var url = self.getTaskUri(taskId);

            var getJSON = function() {
                $.getJSON(url)
                    .done(function (response) {
                        if (response.task_status === 'STARTED' || response.task_status === 'PENDING') {
                            // Task isn't done, so check again
                            if (attempts < 4) {
                                attempts++;
                                getJSON();
                            }
                        } else {
                            // Task done
                            var event_name = 'taskmonitor_' + response.task_name;
                            $(document).trigger({
                                type: event_name,
                                task_id: taskId,
                                task_result: response.task_result
                            });
                        }
                    });
            };
            // Call first time
            getJSON();
        }
    };
})(jQuery, window, document);
