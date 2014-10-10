(function($, window, document, undefined){
    var DTTable;
    window.HLList = {
        config: {
            // DataTables config
            DTSelector: '',
            DTAjaxSource: '',
            DTColumns: '',
            DTDrawCallback: function() {
                // Format checkboxes
                App.initUniform();
                // Truncate long fields
                HLApp.resetTruncateFields();
            },
            DTColumnsDefs: [],
            DTFilterDelay: 250,
            DTServerSide: false,
            DTFilter: true,
            DTPaginationType: 'bootstrap',
            allText: 'All',
            prevText: 'Prev',
            nextText: 'Next',
            recordText: 'Records',
            DTInfoText: 'Showing _START_ to _END_ of _TOTAL_ entries',
            DTSearchText: 'Search:',
            DTLengthMenu: [
                [5, 15, 20, -1],
                [5, 15, 20, 'All'] // change per page values here TODO: 'All' translatable
            ],
            DTDisplayLength: 20,
            DTSorting: [],

            // Export config
            exportColumnsSelector: '.export_columns',
            exportColumnSelector: 'export_column',
            exportCheckBoxes: '#list_column_toggler input[type="checkbox"]',
            exportLinkSelector: '.export_link',
            exportTypeInput: '.export_type',
            exportFilterInput: '.export_filter',
            exportForm: '#form_export',

            // Mass Actions
            groupChangeCheckbox: '.group-checkbox',
            bulkIds: '.bulk-ids',
            actionClass: '.actions',
            checkboxes: '.checkboxes'
        },

        init: function (config) {
            var self = this;
            if (typeof (config === 'object')) {
                $.extend(self.config, config);
            }
            App.initUniform();

            self.setupListeners();
            self.setupFilteringDelay();
            self.setupDataTable();
            self.setupCss();
            self.updateExportColumns();
            $(self.config.actionClass).addClass('disabled');
        },

        setupListeners: function() {
            var self = this,
                cf = self.config;
            $(cf.exportCheckBoxes).on('change', function() {
                self.toggleColumnVisibility.call(self, this);
            });

            $(cf.exportLinkSelector).on('click', function(event) {
                self.exportTable.call(self, this, event);
            });

            $(cf.groupChangeCheckbox).on('change', function() {
                self.toggleGroupCheckbox.call(self, this);
            });

            $(document).on('click', cf.checkboxes, function() {
                self.toggleCheckbox.call(self, this);
            });
        },

        // Datatables

        setupFilteringDelay: function () {
            var self = this;
            $.fn.dataTableExt.oApi.fnSetFilteringDelay = function (oSettings, iDelay) {
                var _that = this;

                // Check if there was a different delay time for filtering set.
                if (iDelay === undefined) {
                    iDelay = self.config.DTFilterDelay;
                }

                this.each(function (i) {
                    $.fn.dataTableExt.iApiIndex = i;
                    var
                        oTimerId = null,
                        sPreviousSearch = null,
                        anControl = $('input', _that.fnSettings().aanFeatures.f);

                    anControl.unbind('keyup search input').bind('keyup search input', function () {
                        if (sPreviousSearch === null || sPreviousSearch != anControl.val()) {
                            window.clearTimeout(oTimerId);
                            sPreviousSearch = anControl.val();
                            oTimerId = window.setTimeout(function () {
                                $.fn.dataTableExt.iApiIndex = i;
                                _that.fnFilter(anControl.val());
                            }, iDelay);
                        }
                    });
                    return this;
                });
                return this;
            };
        },

        setupDataTable: function () {
            var cf = this.config;
            var $container = $(cf.DTSelector);
            var config = {
                aLengthMenu: cf.DTLengthMenu,
                iDisplayLength: cf.DTDisplayLength,
                sPaginationType: cf.DTPaginationType,
                oLanguage: {
                    sLengthMenu: '_MENU_' + cf.recordText,
                    oPaginate: {
                        sPrevious: cf.prevText,
                        sNext: cf.nextText
                    },
                    sInfo: cf.DTInfoText,
                    sSearch: cf.DTSearchText
                },
                bAutoWidth: false,
                aaSorting: cf.DTSorting
            };
            if (cf.DTServerSide) {
                $.extend(config, {
                    bServerSide: true,
                    sAjaxSource: cf.DTAjaxSource,
                    aoColumns: cf.DTColumns,
                    bFilter: cf.DTFilter,
                    fnDrawCallback: cf.DTDrawCallback
                });
            } else {
                $.extend(config, {
                    aoColumnDefs: cf.DTColumnsDefs
                });
            }
            DTTable = $container.dataTable(config).fnSetFilteringDelay();
        },

        setupCss: function() {
            // modify table search input
            $('.dataTables_filter input').addClass('form-control input-small');
            $('.dataTables_length select')
                // modify table per page dropdown
                .addClass('form-control input-xsmall')
                // initialize select2 dropdown
                .select2({minimumResultsForSearch: -1});
        },

        //Export functions

        updateExportColumns: function() {
            //Find all selected columns and updates export field.
            var cf = this.config;
            var selectedColumns = $.map($('input[name="'+ cf.exportColumnSelector +'"]:checked'), function(input) {
                return $(input).val();
            });
            $(cf.exportColumnsSelector).val(selectedColumns.join(','));
        },

        toggleColumnVisibility: function(checkbox) {
            // Get column number which visibility is being toggled.
            var iCol = parseInt($(checkbox).attr('data-column'));
            var bVis = DTTable.fnSettings().aoColumns[iCol].bVisible;
            DTTable.fnSetColumnVis(iCol, (bVis ? false : true));
            // Only visible columns will be exported, update export field.
            this.updateExportColumns();
        },

        exportTable: function(element, event) {
            var cf = this.config;
            // Setup the export type in a field.
            $(cf.exportTypeInput).val($(element).data('export-type'));
            // Keep current search also for export.
            $(cf.exportFilterInput).val(DTTable.fnSettings().oPreviousSearch.sSearch);
            $(cf.exportForm).submit();
            event.preventDefault();
        },

        // Mass actions on tables

        toggleGroupCheckbox: function(checkbox) {
            var self = this;
            var $checkbox = $(checkbox);
            var dataSet = $checkbox.attr('data-set'),
                checked = $checkbox.is(':checked');
            $(dataSet).each(function(id, value) {
                var $parents = $($(value).attr('checked', checked).parents('tr'));
                if(checked) {
                    $parents.addClass('active');
                } else {
                    $parents.removeClass('active');
                }
            });
            $.uniform.update(dataSet);

            self.updateBulkIds();
            self.toggleActionsButton();
        },

        toggleCheckbox: function(checkbox) {
            var self = this;
            $(checkbox).parents('tr').toggleClass('active');
            self.updateBulkIds();
            self.toggleActionsButton();
        },

        updateBulkIds: function() {
            var self = this,
                cf = self.config,
                $groupCheckbox = $(cf.groupChangeCheckbox);
            var selected = $(''+$groupCheckbox.attr('data-set')+':not('+cf.groupChangeCheckbox+'):checked');
            var selectedIds = $.map(selected, function(checkbox) {
                return $(checkbox).val();
            });
            $(cf.bulkIds).val(selectedIds.join(','));

            // set group checkbox unselected if all checkboxes are turned off
            var totalSize = $(cf.checkboxes).filter(':not('+ cf.groupChangeCheckbox+')').size();
            $groupCheckbox.prop('checked', totalSize == selected.length);
            $.uniform.update(cf.groupChangeCheckbox);
        },

        toggleActionsButton: function() {
            var self = this,
                cf = self.config;
            var selected = $(''+$(cf.groupChangeCheckbox).attr('data-set')+':checked');
            if(selected.length) {
                $(cf.actionClass).removeClass('disabled');
            } else {
                $(cf.actionClass).addClass('disabled');
            }
        }
    }
})(jQuery, window, document);
