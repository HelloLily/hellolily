$(function() {
    // initialize uniform checkboxes
    App.initUniform();

    // handle group checkbox toggle
    $('.group-checkbox').change(function() {
        var set = $(this).attr('data-set');
        var checked = $(this).is(':checked');
        $(set).each(function () {
            if(checked) {
                $(this).attr('checked', true);
                $(this).parents('tr').addClass('active');
            } else {
                $(this).attr('checked', false);
                $(this).parents('tr').removeClass('active');
            }
        });
        $.uniform.update(set);

        update_bulk_ids();
        toggle_actions_button();
    });

    // update forms that have actions for selected deals
    function update_bulk_ids() {
        var selected = $(''+$('.group-checkbox').attr('data-set')+':not(.group-checkbox):checked');
        var selectedIds = [];
        for(var i = 0; i < selected.length; i++) {
            selectedIds.push($(selected[i]).val());
        }
        $('.bulk-ids').val(selectedIds.join(','));

        // set group checkbox unselected if all checkboxes are turned off
        var totalSize = $('.checkboxes').filter(':not(.group-checkbox)').size();
        $('.group-checkbox').prop('checked', totalSize == selected.length);
        $.uniform.update('.group-checkbox');
    }

    // handle single checkbox toggle
    $(document).on('click', '.checkboxes', function() {
        $(this).parents('tr').toggleClass('active');
        update_bulk_ids();
        toggle_actions_button();
    });

    // enable/disable actions button when (no) items are selected
    function toggle_actions_button() {
        var selected = $(''+$('.group-checkbox').attr('data-set')+':checked');
        if(selected.length) {
            $('.actions').removeClass('disabled');
        } else {
            $('.actions').addClass('disabled');
        }
    }
    // onload
    update_bulk_ids();
    toggle_actions_button();
});
