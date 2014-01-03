$(function() {
    var tag_field = $('input.tags');
    var tags = [];
    if($(tag_field).data('choices')) {
        tags = $(tag_field).data('choices').split(',');
    }

    tag_field.select2({
        tags: tags,
        tokenSeparators: [",", " "],
    });
});
