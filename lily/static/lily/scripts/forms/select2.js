$(document).ready(function() {
    var tag_field = $('#id_tags');
    var tag_list = tag_field.data('choices').split(',');

    tag_field.select2({tags:tag_list, tokenSeparators: [",", " "]});
});