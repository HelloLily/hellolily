function enableChosen(elem) {
    /* Chosen Select Box Plugin */
    $(elem).find("select.chzn-select:visible").not('.chzn-select-no-search').chosen();
    $(elem).find("select.chzn-select-no-search:visible").chosen({disable_search_threshold: 999999});
}

function enableValidate(elem) {
//    /* JQuery validate plugin */
//    $(elem).validate({
//    success: function (label) {
//        console.log($(label).parent().prev().hasClass('field_error'));
//
//        if( $(label).parent().prev().hasClass('field_error') ) {
//
//        }
//
//        if($(label).parent().prev().hasClass('field_error')) {
//            $(label).parent().prev().children('input').unwrap();
//        }
//        $(label).parent().remove();
//        $(label).remove();
//    },
//
//    errorElement: "li",
//        errorPlacement: function(error, element) {
//            if(!$(element).parent().hasClass('field_error')) {
//                $(element).wrap('<span class="field_error"></span>');
//            }
//            if(!$(element).parent().next().hasClass('mws-error')) {
//                $('<div class="mws-error no_list_style_type"><ul class="errorlist"></ul></div>').insertAfter($(element).parent());
//            }
//            $(element).parent().next().append(error);
//        }
//    });
}

$(document).ready(function () {
    /* Core JS Functions */

    /* Collapsible Panels */
    // $(".mws-panel.mws-collapsible.mws-collapsed .mws-panel-body").css("display", "none");
    // $(".mws-panel.mws-collapsible .mws-panel-header")
    // .append("<div class=\"mws-collapse-button mws-inset\"><span></span></div>")
    // .find(".mws-collapse-button span")
    // .live("click", function(event) {
    // $(this)
    // .parents(".mws-panel")
    // .toggleClass("mws-collapsed")
    // .find(".mws-panel-body")
    // .slideToggle("fast");
    // });

    /* Side dropdown menu */
    $("div#mws-navigation ul li a:not('.i-mailbox'), div#mws-navigation ul li span:not('.spacer')").bind('click', function(event) {
        var ul = $(this).nextAll('ul').eq(0);
        if($(ul).size() !== 0) {
            // do not toggle for followable anchor elements
            if($(this)[0].tagName == 'A') {
                if($(this).attr('href').indexOf('javascript:void(0)') === 0) {
                    event.preventDefault();
                    $(ul).slideToggle('fast', function() {
                        $(this).toggleClass('closed');
                    });
                }
            } else {
                $(ul).slideToggle('fast', function() {
                    $(this).toggleClass('closed');
                });
                event.preventDefault();
            }
        }
    });

    if( $.datepicker ) {
        $.datepicker.setDefaults({
            'dateFormat': 'dd/mm/yy'
        });
    }

    // enable datepicker on rendered fields, hidden fields and fields retrieved with AJAX
    $('form').on('click', '.expected_closing_date.datepicker', function(event){
        if(! $(this).hasClass('hasDatepicker')) {
            $(this).datepicker({ beforeShowDay: $.datepicker.noWeekends });
            $(this).datepicker('show');
        }

        // prevent previously filled in dates to show up in front of the datepicker
        $(this).attr("autocomplete", "off");

        event.preventDefault();
    });

    /* Responsive Layout Script */
    $("div#mws-navigation").live('click', function(event) {
        if(event.target === this || event.target == $("div#mws-navigation > span")[0]) {
            $(this).toggleClass('toggled');
        }
    });

    $("div#mws-navigation #email-search-form input:visible").live('focus', function(event) {
        $(event.target).parent().removeClass('collapsed');
    });

    $("div#mws-navigation #email-search-form input:visible").live('blur', function(event) {
        $(event.target).parent().addClass('collapsed');
    });

    $('div#mws-navigation ul ul li:not(.email-search, .search-results)').hover(
        function(event) {
            $('div#mws-navigation ul ul .hover-state').removeClass('hover-state');
            $(event.target).closest('li').addClass('hover-state');
        },
        function(event) {
            $(event.target).closest('li').removeClass('hover-state');
            $(event.target).closest('li').find('.hover-state').removeClass('hover-state');
        }
    );

    /* Form Messages */
    // $(".mws-form-message").live("click", function() {
    // $(this).animate({opacity:0}, function() {
    // $(this).slideUp("medium", function() {
    // $(this).css("opacity", '');
    // });
    // });
    // });

    /* Message & Notifications Dropdown */
    // $("div#mws-user-tools .mws-dropdown-menu a").click(function(event) {
        // $(".mws-dropdown-menu.toggled").not($(this).parent()).removeClass("toggled");
        // $(this).parent().toggleClass("toggled");
        // event.preventDefault();
    // });

    // $('html').click(function(event) {
        // if($(event.target).parents('.mws-dropdown-menu').size() == 0 ) {
            // $(".mws-dropdown-menu").removeClass("toggled");
        // }
    // });

    /* Side Menu Notification Class */
    // $(".mws-nav-tooltip").addClass("mws-inset");

    /* Table Row CSS Class */
    $("table.mws-table tbody tr:even").addClass("even");
    $("table.mws-table tbody tr:odd").addClass("odd");

    /* Adding title attribute to table header, toolbar buttons and wizard navigation */
    $("table.mws-table thead tr th, .mws-panel-toolbar ul li a, .mws-panel-toolbar ul li a span, .mws-wizard ul li a, .mws-wizard ul li span").each(function() {
        $(this).attr('title', $(this).text());
    });

    /* File Input Styling */
    if($.fn.customFileInput) {
        $("input[type='file']").customFileInput();
    }

    /* Chosen */
    if($.fn.chosen) {
        enableChosen($('body'));
    }

    /* Elastic (auto grow) */
    if( $.fn.elastic ) {
        $('textarea:visible').elastic();
    }

    /* Tooltips */
    // if($.fn.tipsy) {
        // var gravity = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'];
        // for(var i in gravity)
        // $(".mws-tooltip-"+gravity[i]).tipsy({gravity: gravity[i]});
    //
    // $('input[title], select[title], textarea[title]').tipsy({trigger: 'focus', gravity: 'w'});
    // }

    /* Dual List Box */
    // if($.configureBoxes) {
        // $.configureBoxes();
        // }

    /* Placeholders for browsers without support for the placeholder attribute */
    if($.fn.placeholder) {
        $('[placeholder]').placeholder();
    }

    /* Enable tabs on this class */
    if($.fn.tabs) {
        $(".mws-tabs").tabs();
    }

    /* Submit the form on ctrl + enter in any input field (including textarea/checkbox/radiobutton/select) */
    $('form.mws-form :input').live('keydown', function(event) {
        var form = $(this).closest('form');
        submit_form_on_ctrl_enter(event, form);
    });

    /* Re-index tabbale elements on page load */
    if($.tabthisbody) {
        $.tabthisbody();
    }

    /* Defaults for jGrowl */
    if($.jGrowl) {
        $.jGrowl.defaults.closerTemplate = '<div>[ close all ]</div>';
        $.jGrowl.defaults.position = 'bottom-right';
        $.jGrowl.defaults.sticky = false;
        $.jGrowl.defaults.glue = 'after';
        $.jGrowl.defaults.themeState = '';
        $.jGrowl.defaults.pool = 2;
        $.jGrowl.defaults.beforeOpen = function(notification,message,o,container) {
            if( $(notification).find('a').length == 0 ) {
                $(notification).click(function() {
                    $(this).trigger('jGrowl.beforeClose');
                });
            } else {
                $(notification).dblclick(function () {
                    $(this).trigger('jGrowl.beforeClose');
                });
            }
        };
    }

    /* General config for delete dialog */
    if($.fn.dialog) {
        // delete account
        $('.link.delete').click(function (event) {
            var pkRegex = new RegExp('(\\d+)');
            var pk = pkRegex.exec($(this).attr('id'));
            var dialog = $('#dialog-' + pk)[0];
            if (dialog) {
                $('#dialog-' + pk).dialog('open');
            } else {
                var location = $(this).attr('href');
                $('#dialog-delete-generic form').attr('action', location);
                $('#dialog-delete-generic').dialog('open');
            }
            event.preventDefault();
        });

        // transform div into delete dialog
        $('.dialog.delete, #dialog-delete-generic').dialog({
            autoOpen: false,
            modal: true,
            width: 350,
            buttons: [
            {
                'class': 'mws-button red float-left',
                text: gettext('No'),
                click: function() {
                    // cancel form on NO
                    $(this).dialog('close');
                }
            },
            {
                'class': 'mws-button green',
                text: gettext('Yes'),
                click: function() {
                    // submit form on YES
                    $(this).find('form').submit();
                }
            }
            ]
        });

        $("#loadingDialog").dialog({
            autoOpen: false,
            title: gettext('Please wait...'),
            modal: true,
            width: "320",
            closeOnEscape: false,
            resizable: false,
            open: function(event, ui) {
                $(this).parent().children().children('.ui-dialog-titlebar-close').hide();
            }
        });

        $("#successDialog").dialog({
            autoOpen: false,
            title: gettext('Success'),
            modal: true,
            width: "320",
            buttons: [{
            text: gettext('Close'),
            click: function() {
            $( this ).dialog( "close" );
            }}]
        });

        $("#errorDialog").dialog({
            autoOpen: false,
            title: gettext('Error'),
            modal: true,
            width: "320",
            buttons: [{
                text: gettext('Close'),
                click: function() {
                    $( this ).dialog( "close" );
            }}]
        });
    }

//    $('form').validate({
//        rules: {
//            input: {
//                required: true,
//            }
//        },
//        submitHandler: function(form) {
//            console.log('valid');
//        },
//        invalidHandler: function(form, validator) {
//            console.log('invalid');
//        }
//    });

    if($.fn.validate) {
        $("form").each(function () {
            enableValidate($(this));
        });
    }

    if($.fn.password_strength) {
        // keep track of password strength
        $('#id_password, #id_new_password1').password_strength({
            'minLength':6,
            'container':'#password_strength',
            'textContainer':'#password-text',
            'texts':{
                1:gettext('Too weak'),
                2:gettext('Weak password'),
                3:gettext('Normal strength'),
                4:gettext('Strong password'),
                5:gettext('Very strong password')
            }
        });
    }

    function toggleDropDownIcons() {
        // point sideways, all closed and active dropdown triggers
        $('#mws-navigation ul ul li.active > a.mws-dropdown-trigger + span + ul.closed').prevAll('.mws-dropdown-trigger').find('.ui-icon')
            .removeClass('ui-icon-carat-1-e')  // not having this css-class prevents removing triangle-s on mouseout
            .removeClass('ui-icon-triangle-1-s')
            .addClass('ui-icon-triangle-1-e');

        // point sideways, all inactive dropdown triggers
        $('#mws-navigation ul ul a.mws-dropdown-trigger:not(li.active > a.mws-dropdown-trigger) + span + ul.closed').prevAll('.mws-dropdown-trigger').find('.ui-icon')
            .removeClass('ui-icon-triangle-1-s')
            .removeClass('ui-icon-triangle-1-e')
            .addClass('ui-icon-carat-1-e');  // shows triangle-1-e on mouseover

        // point downwards, all open dropdown triggers (inactive or active)
        $('#mws-navigation ul ul li .mws-dropdown-trigger + span + ul:not(.closed)').prevAll('.mws-dropdown-trigger').find('.ui-icon')
            .removeClass('ui-icon-triangle-1-e')
            .addClass('ui-icon-triangle-1-s')
            .addClass('ui-icon-carat-1-e');

        // point downwards, all open and active dropdown triggers
        $('#mws-navigation ul ul li.active > a.mws-dropdown-trigger + span + ul:not(.closed)').prevAll('.mws-dropdown-trigger').find('.ui-icon')
            .removeClass('ui-icon-carat-1-e')  // not having this css-class prevents removing triangle-s on mouseout
            .removeClass('ui-icon-triangle-1-e')
            .addClass('ui-icon-triangle-1-s');
    }

    function toggleOpenMenus(element) {
        // element should be a.mws-dropdown-trigger

        // close all UL's except the one next to element and parents
        var parents = Array();
        parents.push($(element).closest('ul')[0]); // parent UL
        parents.push($(element).nextAll('ul').eq(0)[0]);  // current

        $('#mws-navigation ul ul li ul').filter(function() {
            // get every UL, except current/parent
            return $(parents).index($(this)) < 0;
        }).hide().addClass('closed').closest('.expanded').removeClass('expanded').find('.expanded').removeClass('expanded'); // close all these UL's
    }

    $('div#mws-navigation ul li .mws-dropdown-trigger').click(function(event) {
        // event.target == a.mws-dropdown-trigger

        // go to url for every anchor, except when it has a script url
        if($(event.target).attr('href').indexOf('javascript:void(0)') === 0) {
            // if it has, only change the icon and expand the sub menu
            toggleOpenMenus($(event.target));
            toggleDropDownIcons();
        }
        $(event.target).closest('li').toggleClass('expanded');
    });

    $('div#mws-navigation ul li .mws-dropdown-trigger i.ui-icon').click(function(event) {
        // event.target == i.ui-icon.ui-icon-carat-1-?
        toggleOpenMenus($(event.target).parent());

        // slide in/out
        $(event.target).closest('li').toggleClass('expanded');
        $(event.target).parent().nextAll('ul').eq(0).slideToggle('fast', function() {
            $(this).toggleClass('closed');
            toggleDropDownIcons();
        });

        event.preventDefault();
        event.stopPropagation();  // when propagating event.target does not match a.mws-dropdown-trigger which confuses the click handler for these anchor elements
    });

    $('div#mws-navigation ul li .mws-dropdown-trigger i.ui-icon').hover(
        function(event) {
            if(!$(event.target).hasClass('ui-icon-triangle-1-s')) {
                $(event.target).addClass('ui-icon-triangle-1-e');
            }
        },
        function(event) {
            if($(event.target).hasClass('ui-icon-carat-1-e')) {
                $(event.target).removeClass('ui-icon-triangle-1-e');
            }
        }
    );
});
