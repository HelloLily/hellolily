(function($, window, document, undefined) {
    var currentStage;

    window.HLDeals = {
        config: {
            dealsUpdateStageUrl: '/deals/update/stage/',
            statusSpan: '#status',
            dealDiv: '#deal-stage',
            closedDateSpan: '#closed-date',
            expectedClosedDateSpan: '#expected-closing-date'
        },

        init: function (config) {
            // Setup config
            var self = this;
            if ($.isPlainObject(config)) {
                $.extend(self.config, config);
            }
            self.initListeners();
            self.setCurrentStage();
        },

        initListeners: function () {
            var self = this,
                cf = self.config;

            $(cf.dealDiv).on('click', function (event) {
                self.changeStage.call(self, event);
            });
        },

        setCurrentStage: function() {
            currentStage = $('input[name=radio]:checked', this.config.dealDiv).closest('label').attr('for');
        },

        changeStage: function(event) {
            var self = this,
                cf = self.config;
            var $radio_element = $('#' + $(event.target).closest('label').attr('for'));
            if($radio_element.attr('id') != currentStage) {
                // try this
                $.ajax({
                    url: cf.dealsUpdateStageUrl + $radio_element.closest(cf.dealDiv).data('object-id') + '/',
                    type: 'POST',
                    data: {
                        'stage': $radio_element.val()
                    },
                    beforeSend: HLApp.addCSRFHeader,
                    dataType: 'json'
                }).done(function(data) {
                    currentStage = $radio_element.attr('id');
                    $(cf.statusSpan).text(data.stage);
                    // check for won/lost and closing date
                    if(data.closed_date) {
                        $(cf.closedDateSpan).text(data.closed_date).removeClass('hide');
                        $(cf.expectedClosedDateSpan +':visible').addClass('hide');
                    } else {
                        $(cf.closedDateSpan).text('');
                        $(cf.closedDateSpan + ':visible').addClass('hide');
                        $(cf.expectedClosedDateSpan).removeClass('hide');
                    }
                    // loads notifications if any
                    load_notifications();
                }).fail(function() {
                    // reset selected stage
                    $radio_element.attr('checked', false);
                    $radio_element.closest('label').removeClass('active');
                    $('#' + currentStage).attr('checked', true).closest('label').addClass('active');
                    // loads notifications if any
                    load_notifications();
                });
            }
        }
    }
})(jQuery, window, document);
