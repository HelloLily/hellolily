(function($, window, document, undefined) {
    var currentStatus;

    window.HLCases = {
        config: {
            caseUpdateUrl: '/cases/update/status/',
            caseUpdateAssignedToUrl: '/cases/update/assigned_to/',
            caseId: null,
            statusSpan: '#status',
            statusDiv: '#case-status',
            parcelProviderSelect: '#id_parcel_provider',
            parcelIdentifierInput: '#id_parcel_identifier',
            assignedToField: '#id_assigned_to',
            assignToMeButton: '.assign-me-btn',
            currentAssignedTo: null
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

            $(cf.assignToMeButton).on('click', function() {
                self.changeAssignedTo.call(self, this);
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
                if (cf.caseId != null) {
                    $.ajax({
                        url: cf.caseUpdateUrl + cf.caseId + '/',
                        type: 'POST',
                        data: {
                            status: $radio_element.val()
                        },
                        beforeSend: HLApp.addCSRFHeader,
                        dataType: 'json'
                    }).done(function (data) {
                        currentStatus = $radio_element.attr('id');
                        $(cf.statusSpan).text(data.status);
                        // loads notifications if any
                        load_notifications();
                    }).fail(function () {
                        // reset selected status
                        $(radio_element).attr('checked', false).closest('label').removeClass('active');
                        $('#' + currentStatus).attr('checked', true).closest('label').addClass('active');
                        // loads notifications if any
                        load_notifications();
                    });
                }
            }
        },

        changedParcelProviderSelect: function(select) {
            // Remove identifier if the provider is removed
            var $select = $(select);
            if (!$select.val()) {
                $(this.config.parcelIdentifierInput).val('');
            }
        },

        changeAssignedTo: function () {
            var self = this,
                cf = self.config;

            var assignee = null;

            if (cf.currentAssignedTo != currentUser.id) {
                assignee = currentUser.id;
            }

            if (cf.caseId != null) {
                $.ajax({
                    url: cf.caseUpdateAssignedToUrl + cf.caseId + '/',
                    type: 'POST',
                    data: {
                        assignee: assignee
                    },
                    beforeSend: HLApp.addCSRFHeader,
                    dataType: 'json'
                }).done(function (data) {
                    var assignee = data.assignee;

                    // TODO: This will be made prettier once we Angularify the detail page(s)
                    if (assignee) {
                        $('.summary-data.assigned-to').html(data.assignee.name);
                        $('.assign-me-btn').html('Unassign');
                        cf.currentAssignedTo = data.assignee.id;
                    }
                    else {
                        $('.summary-data.assigned-to').html('Unassigned');
                        $('.assign-me-btn').html('Assign to me');
                        cf.currentAssignedTo = null;
                    }
                }).always(function () {
                    // loads notifications if any
                    load_notifications();
                });
            }
        },

        addAssignToMeButton: function() {
            var self = this;
            var assignToMeButton = $('<button class="btn btn-link assign-me-btn">Assign to me</button>');

            $(self.config.assignedToField).after(assignToMeButton);

            assignToMeButton.click(function (event) {
                event.preventDefault();
                $(self.config.assignedToField).val(currentUser.id).change();
            });
        }
    }
})(jQuery, window, document);
