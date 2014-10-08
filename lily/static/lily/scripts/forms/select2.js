/* Library with Select2 functions */

/* Make tag input fields taggable */
function init_select2_tags() {
    var tag_field = $('input.tags');
    var tags = [];
    if($(tag_field).data('choices')) {
        tags = $(tag_field).data('choices').split(',');
    }

    tag_field.select2({
        tags: tags,
        tokenSeparators: [",", " "]
    });
}

/* Setup Select2 fields with remote data */
function init_select2_ajax() {
    var page_limit = 30;
    $('.select2ajax').each(function(){
        $(this).select2({
            ajax: {
                quietMillis: 300,
                cache: true,
                data: function (term, page) { // page is the one-based page number tracked by Select2
                    return {
                        q: term, //search term
                        page_limit: page_limit, // page size
                        page: page, // page number
                        filter: $('#'+$(this).data('filter-on')).val()
                    };
                },
                results: function (data, page) {
                    var more = (page * page_limit) < data.total; // whether or not there are more results available
                    // Add clear option
                    if (page == 1) {
                        data.objects.unshift({id: -1, text:'-- Clear --'});
                    }
                    return {
                        results: data.objects,
                        more: more
                    }
                }
            },
            initSelection: function (item, callback) {
                var id = item.val();
                var text = item.data('selected-text');
                var data = { id: id, text: text };
                callback(data);
            }
        });
    });
}

/* Select fields automatic to select2 forms */
function init_select2() {
    $('select').select2({
        // at least this many results are needed to enable the search field
        // (9 is the amount at which the user must scroll to see all items)
        minimumResultsForSearch: 9
    });

    // Initialize Select2 input fields that require remote Ajax calls
    init_select2_ajax();

    // Initialze Select2 tags for the tag fields
    init_select2_tags();
}



$(function($) {
    // Initialize all select2 on body load
	init_select2();

    // On modal popup
    $('body').on('shown.bs.modal', '.modal', function() {
        init_select2();
    });
});
