$(function($){
    // Setup the columns that will be exported.
    updateExportColumns();

    $('#list_column_toggler input[type="checkbox"]').change(function() {
        /* Get the DataTables object again - this is not a recreation, just a get of the object */
        var oTable = $('.page-content .data-table').dataTable();
        // Get column number which visibility is being toggled.
        var iCol = parseInt($(this).attr("data-column"));
        var bVis = oTable.fnSettings().aoColumns[iCol].bVisible;
        oTable.fnSetColumnVis(iCol, (bVis ? false : true));
        // Only visible columns will be exported, update export field.
        updateExportColumns();
    });

    $('.export_link').click(function(elem) {
        /* Get the DataTables object again - this is not a recreation, just a get of the object */
        var oTable = $('.page-content .data-table').dataTable();
        // Setup the export type in a field.
        $('.export_type').val($(this).data('export-type'));
        // Keep current search also for export.
        $('.export_filter').val(oTable.fnSettings().oPreviousSearch.sSearch);
        $('#form_export').submit();
        elem.preventDefault();
    });

    function updateExportColumns() {
        /*
        Find all selected columns and updates export field.
         */
        var exportColumnsInput = $('.export_columns');
        if(exportColumnsInput.length) {
            var selected = $('input[name="export_column"]:checked');
            var selectedColumns = [];
            for(var i = 0; i < selected.length; i++) {
                selectedColumns.push($(selected[i]).val());
            }
            exportColumnsInput.val(selectedColumns.join(','));
        }
    }
});
