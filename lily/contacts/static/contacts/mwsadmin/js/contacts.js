
// TODO: set focus on first element a form error was detected
// TODO: select first e-mail as primary when deleting primary

$(document).ready(function() {
    // set focus on first name
    set_focus('id_first_name');

    // manually add hover classes when hovering over a label element
    $('.email_is_primary label span').live({
        mouseenter: function() {
            $(this).addClass('state-hover');
        },
        mouseleave: function() {
            $(this).removeClass('state-hover');
        }
    });

    // change selected primary e-mailadres
    $('.email_is_primary label span').live('click', function() {
        // find elements
        formset = $(this).closest('.mws-form-row');
        input_siblings = $(formset).find('.email_is_primary label input');

        // uncheck others
        $(input_siblings).siblings('span').removeClass('checked');

        // check this one
        $(this).addClass('checked');
    });

    // update e-mail formset to select first as primary
    // $('.email_is_primary input[name$="primary-email"]:first').attr('checked', 'checked').siblings('span').addClass('checked');

    function reload_email_share_wizard() {
        var wrapped_div = $('#dialog-email-share-wizard [name="user_group"]').closest('.mws-form-row');
        if($('#dialog-email-share-wizard [name="shared_with"]:checked').val() < 2) {
            $(wrapped_div).hide();
        } else {
            $(wrapped_div).show();
        }
        enableChosen($('#dialog-email-share-wizard'));
    }

    // open dialog for sharing options for e-mail address
    $('.email_addresses .email-share-wizard a').live('click', function(event) {
        $('#dialog-email-share-wizard').dialog('destroy');
        var id = 'new';
        var id_input = $(event.target).closest('.email_addresses').find('input[id$="id"]');
        if( id_input.length ) {
            id = $(id_input).val();
        }
        var url = '/messaging/email/account/wizard/share/';
        $('#dialog-email-share-wizard').load(
            url + id + '/',
            function() {
                // transform div into email share options dialog
                $('#dialog-email-share-wizard')
                    .dialog({ // init dialog
                        autoOpen: false,
                        modal: true,
                        width: 600,
                        height: 400,
                        resizable: true,
                        buttons: [
                        {
                            'class': 'mws-button red float-left',
                            text: gettext('Cancel'),
                            click: function() {
                                // cancel form on NO
                                $(this).dialog('close');
                            }
                        },
                        {
                            'class': 'mws-button green',
                            text: gettext('Save'),
                            click: function() {
                                // submit form on YES
                                $(this).find('form').ajaxSubmit({
                                    type: 'post',
                                    dataType: 'json',
                                    url: url + id + '/',
                                    success: function(response) {
                                        if(response.error) {
                                            $('#dialog-email-share-wizard').find('form').html(response.html);
                                            reload_email_share_wizard();
                                        } else {
                                           if( $.jGrowl ) {
                                                if( response.notification ) {
                                                    for(i=0; i < response.notification.length; i++) {
                                                        $.jGrowl(response.notification[i].message, {
                                                            theme: response.notification[i].tags
                                                        });
                                                    }
                                                }
                                            }
                                            $('#dialog-email-share-wizard').dialog('close');
                                        }
                                    },
                                    error: function(response){
                                        $("#errorDialog").dialog('open');
                                    }
                                });
                            }
                        }
                        ]
                    }) // bind callback
                    .live('dialogopen', function(event, ui) {
                        reload_email_share_wizard();
                    }) // open dialog
                    .dialog('open');
            }
        );
    });

    $('#dialog-email-share-wizard [name="shared_with"]').live('change', function() {
        reload_email_share_wizard();
    });

    // open configuration wizard for e-mail address
    $('.email_addresses .email-configuration-wizard a').live('click', function(event) {
        var id = 'new';
        var id_input = $(event.target).closest('.email_addresses').find('input[id$="id"]');
        if( id_input.length ) {
            id = $(id_input).val();
        }
        var url = '/messaging/email/account/wizard/configuration/';
        $('#dialog-email-configuration-wizard').load(
            url,
            function() {
                // $('#dialog-email-configuration-wizard').html('');
                $('#dialog-email-configuration-wizard').smartWizard({
                    contentURL: url + id + '/',
                    transitionEffect: 'dont',
                    contentCache: false,
                    onLeaveStep: function(obj, curStep) {
                        // clear form errors from past steps
                        $(obj).parent('.stepContainer').find('.mws-error').remove();
                        $(obj).parent('.stepContainer').find('.field_error').removeClass('field_error');
                        return true;
                    },
                    onShowStep: function(obj) {
                        // enable chosen for select elements (if any)
                        enableChosen($($(obj).attr('href')));
                    },
                    onFinish: function(obj) {
                        $('#dialog-email-configuration-wizard').dialog('close');
                    }
                });
                $('#dialog-email-configuration-wizard').dialog('open');
            }
        );
    });

    // preload server settings
    $('#dialog-email-configuration-wizard [name="1-presets"]').live('change', function() {
        try {
            var prefix = '1-';
            var json = $('#dialog-email-configuration-wizard [name="' + prefix + 'presets"] :selected').data('serialized');
            if(json) {
                $.each(json, function(name, value) {
                    // set value according to type of field
                    var re = /^(?:color|date|datetime|email|hidden|month|number|password|range|search|tel|text|time|url|week)$/i; // matches <input />
                    var input = $('#dialog-email-configuration-wizard [name="' + prefix + name + '"]')[0];
                    var t = input.type, tag = input.tagName.toLowerCase();
                    if (re.test(t) || tag == 'textarea') {
                        input.value = value;
                    }
                    else if (t == 'checkbox' || t == 'radio') {
                        input.checked = value;
                    }
                    else if (tag == 'select') {
                        input.selectedIndex = value;
                    }
                });
            } else {
                $('#dialog-email-configuration-wizard :input').clearFields();
            }
        } catch(error) {
            $('#dialog-email-configuration-wizard :input').clearFields();
        }
    });

    $('#dialog-email-configuration-wizard').dialog({
        autoOpen: false,
        modal: true,
        width: 600,
        resizable: false
    });
});
