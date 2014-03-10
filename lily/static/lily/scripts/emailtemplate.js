$(function($) {
    var update_variable_options = function() {
        var value_select = $('#id_values');
        var category = $('#id_variables').val();

        value_select.find("option").not('option[value=""]').remove();
        value_select.change();

        if (category !== '') {
            $.each(parameter_choices[category], function(parameter, label) {
                value_select.append($("<option>", {
                    value: parameter,
                    text: label
                }));
            });
        }
    };
    /* on change */
    $('#id_variables').change(update_variable_options);
    /* on load */
    update_variable_options();

    $('#id_insert_button').click(function(event) {
        var textvalue = $('#id_text_value').html();
        var wedit = $('#id_body_html').data("wysihtml5").editor;
        wedit.focus();
        wedit.composer.commands.exec("insertHTML", textvalue);

        event.preventDefault();
    });

    $('#body_file_upload').click(function(event) {
        $('#id_body_file').click();

        event.preventDefault();
    });
});
