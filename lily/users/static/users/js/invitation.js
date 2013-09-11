

$(document).ready(function() {
    function bindFormset() {
        $('.mws-form-formset').formset({
            formTemplate: '.formset-custom-template',
            prefix: 'form',
            addText: gettext('Add another'),
            preventEmptyFormset: true,
            added: function() { $.tabthisbody(); },
            addCssClass: 'add-row mws-form-row',
            deleteCssClass: 'invitation-delete-row',
        });
    }
    bindFormset();
    
    $("#mws-form-dialog").dialog({
        autoOpen: false, 
        title: gettext('User invitation form'), 
        modal: true, 
        width: "640", 
        buttons: [{
            text: gettext('Send invitation(s)'), 
            click: function() { sendForm($( this )); }
        }],
        close: function(event, ui) { clearForm($(this).find('form.mws-form')); }
    });
    
    $("#mws-form-dialog-mdl-btn").bind("click", function(event) {
        $("#mws-form-dialog").dialog("open");
        event.preventDefault();
    });
});