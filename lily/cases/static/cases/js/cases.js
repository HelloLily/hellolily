(function($, window, document, undefined) {
    var currentStatus;

    window.HLCases = {
        config: {
            caseUpdateUrl: '/cases/update/status/',
            statusSpan: '#status',
            statusDiv: '#case-status',
            parcelProviderSelect: '#id_parcel_provider',
            parcelIdentifierInput: '#id_parcel_identifier'
        },

        init: function(config) {
            // Setup config
            var self = this;
            if ($.isPlainObject(config)) {
                $.extend(self.config, config);
            }
            self.initListeners();
            self.setCurrentStatus();
        },

        initListeners: function() {
            var self = this,
                cf = self.config;

            $(cf.statusDiv).on('click', function(event) {
               self.changeStatus.call(self, event);
            });

            $(cf.parcelProviderSelect).on('change', function() {
               self.changedParcelProviderSelect.call(self, this);
            });
        },

        setCurrentStatus: function() {
            currentStatus = $('input[name=radio]:checked', this.config.statusDiv).closest('label').attr('for');
        },

        changeStatus: function(event) {
            var self = this,
                cf = self.config;
            var radio_element = $('#' + $(event.target).closest('label').attr('for'));
            if(radio_element.attr('id') != currentStatus) {
                var $radio_element = $(radio_element);
                $.ajax({
                    url: cf.caseUpdateUrl + $radio_element.closest(cf.statusDiv).data('object-id') + '/',
                    type: 'POST',
                    data: {
                        'status': $radio_element.val()
                    },
                    beforeSend: HLApp.addCSRFHeader,
                    dataType: 'json'
                }).done(function(data) {
                    currentStatus = $radio_element.attr('id');
                    $(cf.statusSpan).text(data.status);
                    // loads notifications if any
                    load_notifications();
                }).fail(function() {
                    // reset selected status
                    $(radio_element).attr('checked', false).closest('label').removeClass('active');
                    $('#' + currentStatus).attr('checked', true).closest('label').addClass('active');
                    // loads notifications if any
                    load_notifications();
                });
            }
        },

        changedParcelProviderSelect: function(select) {
            // Remove identifier if the provider is removed
            var $select = $(select);
            if (!$select.val()) {
                $(this.config.parcelIdentifierInput).val('');
            }
        }
    }
})(jQuery, window, document);
