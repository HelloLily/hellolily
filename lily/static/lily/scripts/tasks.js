(function ($, window, document, undefined) {
    window.HLTasks = {
        config: {
            placeholderUrl: '/taskmonitor/task/status/000/',
            sendMessageSuccess: {message: 'I successfully delivered your e-mail!', title: 'Yay!'},
            sendMessageError: {message: 'Sorry, I couldn\'t deliver your e-mail, but I did save it as a draft so you can try again later.', title: 'Oops!'},
            saveMessageSuccess: {message: 'I successfully saved your message as a draft!', title: 'Yay!'},
            saveMessageError: {message: 'I couldn\'t save your message as a draft, please try again!', title: 'Oops!'}
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
                })
                .on('taskmonitor_save_message', function (event) {
                    if (event.task_result) {
                        toastr.success(cf.saveMessageSuccess.message, cf.saveMessageSuccess.title);
                    } else {
                        toastr.error(cf.saveMessageError.message, cf.saveMessageError.title);
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
