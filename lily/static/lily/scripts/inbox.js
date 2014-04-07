var Inbox = function () {

//     var content = $('.inbox-content');
//     var loading = $('.inbox-loading');

    // var loadInbox = function (el, name) {
    //     var url = 'inbox_inbox.html';
    //     var title = $('.inbox-nav > li.' + name + ' a').attr('data-title');

    //     loading.show();
    //     content.html('');
    //     toggleButton(el);

    //     $.ajax({
    //         type: "GET",
    //         cache: false,
    //         url: url,
    //         dataType: "html",
    //         success: function(res)
    //         {
    //             toggleButton(el);

    //             $('.inbox-nav > li.active').removeClass('active');
    //             $('.inbox-nav > li.' + name).addClass('active');
    //             $('.inbox-header > h1').text(title);

    //             loading.hide();
    //             content.html(res);
    //             App.fixContentHeight();
    //             App.initUniform();
    //         },
    //         error: function(xhr, ajaxOptions, thrownError)
    //         {
    //             toggleButton(el);
    //         },
    //         async: false
    //     });
    // }

    // var loadMessage = function (el, name, resetMenu) {
    //     var url = 'inbox_view.html';

    //     loading.show();
    //     content.html('');
    //     toggleButton(el);

    //     $.ajax({
    //         type: "GET",
    //         cache: false,
    //         url: url,
    //         dataType: "html",
    //         success: function(res)
    //         {
    //             toggleButton(el);

    //             if (resetMenu) {
    //                 $('.inbox-nav > li.active').removeClass('active');
    //             }
    //             $('.inbox-header > h1').text('View Message');

    //             loading.hide();
    //             content.html(res);
    //             App.fixContentHeight();
    //             App.initUniform();
    //         },
    //         error: function(xhr, ajaxOptions, thrownError)
    //         {
    //             toggleButton(el);
    //         },
    //         async: false
    //     });
    // }

    var customParser = (function() {
        function parse(elementOrHtml, rules, context, cleanUp) {
            return elementOrHtml;
        }
        return parse;
        })();

    var initWysihtml5 = function () {
        $('.inbox-wysihtml5').wysihtml5({
            "stylesheets": [media_url('wysiwyg-color.css')],
            "font-styles": true, //Font styling, e.g. h1, h2, etc.
            "color": false, //Button to change color of font
            "emphasis": true, //Italics, bold, etc.
            "lists": true, //(Un)ordered lists, e.g. Bullets, Numbers.
            "html": true, //Button which allows you to edit the generated HTML.
            "link": true, //Button to insert a link.
            "image": false, //Button to insert an image.
            parser: customParser,
        });
    };

    // var initFileupload = function () {

    //     $('#fileupload').fileupload({
    //         // Uncomment the following to send cross-domain cookies:
    //         //xhrFields: {withCredentials: true},
    //         url: 'assets/plugins/jquery-file-upload/server/php/',
    //         autoUpload: true
    //     });

    //     // Upload server status check for browsers with CORS support:
    //     if ($.support.cors) {
    //         $.ajax({
    //             url: 'assets/plugins/jquery-file-upload/server/php/',
    //             type: 'HEAD'
    //         }).fail(function () {
    //             $('<span class="alert alert-error"/>')
    //                 .text('Upload server currently unavailable - ' +
    //                 new Date())
    //                 .appendTo('#fileupload');
    //         });
    //     }
    // }

    // var loadCompose = function (el) {
    //     var url = 'inbox_compose.html';

    //     loading.show();
    //     content.html('');
    //     toggleButton(el);

    //     // load the form via ajax
    //     $.ajax({
    //         type: "GET",
    //         cache: false,
    //         url: url,
    //         dataType: "html",
    //         success: function(res)
    //         {
    //             toggleButton(el);

    //             $('.inbox-nav > li.active').removeClass('active');
    //             $('.inbox-header > h1').text('Compose');

    //             loading.hide();
    //             content.html(res);

    //             initFileupload();
    //             initWysihtml5();

    //             $('.inbox-wysihtml5').focus();
    //             App.fixContentHeight();
    //             App.initUniform();
    //         },
    //         error: function(xhr, ajaxOptions, thrownError)
    //         {
    //             toggleButton(el);
    //         },
    //         async: false
    //     });
    // }

    // var loadReply = function (el) {
    //     var url = 'inbox_reply.html';

    //     loading.show();
    //     content.html('');
    //     toggleButton(el);

    //     // load the form via ajax
    //     $.ajax({
    //         type: "GET",
    //         cache: false,
    //         url: url,
    //         dataType: "html",
    //         success: function(res)
    //         {
    //             toggleButton(el);

    //             $('.inbox-nav > li.active').removeClass('active');
    //             $('.inbox-header > h1').text('Reply');

    //             loading.hide();
    //             content.html(res);
    //             $('[name="message"]').val($('#reply_email_content_body').html());

    //             handleCCInput(); // init "CC" input field

    //             initFileupload();
    //             initWysihtml5();
    //             App.fixContentHeight();
    //             App.initUniform();
    //         },
    //         error: function(xhr, ajaxOptions, thrownError)
    //         {
    //             toggleButton(el);
    //         },
    //         async: false
    //     });
    // }

    // var loadSearchResults = function (el) {
    //     var url = 'inbox_search_result.html';

    //     loading.show();
    //     content.html('');
    //     toggleButton(el);

    //     $.ajax({
    //         type: "GET",
    //         cache: false,
    //         url: url,
    //         dataType: "html",
    //         success: function(res)
    //         {
    //             toggleButton(el);

    //             $('.inbox-nav > li.active').removeClass('active');
    //             $('.inbox-header > h1').text('Search');

    //             loading.hide();
    //             content.html(res);
    //             App.fixContentHeight();
    //             App.initUniform();
    //         },
    //         error: function(xhr, ajaxOptions, thrownError)
    //         {
    //             toggleButton(el);
    //         },
    //         async: false
    //     });
    // }

    var handleCCInput = function () {
        var the = $('.inbox-compose .mail-to .inbox-cc');
        var input = $('.inbox-compose .input-cc');
        the.hide();
        input.show();
        $('.close', input).click(function () {
            input.hide();
            the.show();
        });
    };

    var handleBCCInput = function () {

        var the = $('.inbox-compose .mail-to .inbox-bcc');
        var input = $('.inbox-compose .input-bcc');
        the.hide();
        input.show();
        $('.close', input).click(function () {
            input.hide();
            the.show();
        });
    };

    // var toggleButton = function(el) {
    //     if (typeof el == 'undefined') {
    //         return;
    //     }
    //     if (el.attr("disabled")) {
    //         el.attr("disabled", false);
    //     } else {
    //         el.attr("disabled", true);
    //     }
    // }

    return {
        //main function to initiate the module
        init: function () {

    //         // handle compose btn click
    //         $('.inbox .compose-btn a').live('click', function () {
    //             loadCompose($(this));
    //         });

    //         // handle reply and forward button click
    //         $('.inbox .reply-btn').live('click', function () {
    //             loadReply($(this));
    //         });

    //         // handle view message
    //         $('.inbox-content .view-message').live('click', function () {
    //             loadMessage($(this));
    //         });

    //         // handle inbox listing
    //         $('.inbox-nav > li.inbox > a').click(function () {
    //             loadInbox($(this), 'inbox');
    //         });

    //         // handle sent listing
    //         $('.inbox-nav > li.sent > a').click(function () {
    //             loadInbox($(this), 'sent');
    //         });

    //         // handle draft listing
    //         $('.inbox-nav > li.draft > a').click(function () {
    //             loadInbox($(this), 'draft');
    //         });

    //         // handle trash listing
    //         $('.inbox-nav > li.trash > a').click(function () {
    //             loadInbox($(this), 'trash');
    //         });

            //handle compose/reply cc input toggle
            $('.inbox-compose .mail-to .inbox-cc').live('click', function () {
                handleCCInput();
            });

            //handle compose/reply bcc input toggle
            $('.inbox-compose .mail-to .inbox-bcc').live('click', function () {
                handleBCCInput();
            });

    //         //handle loading content based on URL parameter
    //         if (App.getURLParameter("a") === "view") {
    //             loadMessage();
    //         } else if (App.getURLParameter("a") === "compose") {
    //             loadCompose();
    //         } else {
    //            $('.inbox-nav > li.inbox > a').click();
    //         }

            initWysihtml5();
            App.fixContentHeight();
            App.initUniform();

        }

    };

}();

$(function($) {
    // open single message
    $('.inbox-content .view-message').click(function () {
        $('.inbox-content').hide();
        $('.inbox-loading').show();
        redirect_to($(this).closest('[data-href]').data('href'));
    });

    var frame = $('.inbox-view iframe')[0];
    function email_frame_autogrow() {
        setTimeout(function() {
            $('.inbox-loading').hide();
            $('.inbox-view').show();
            App.fixContentHeight();

            // highlight selected messages
            $('.mail-checkbox:not(.mail-group-checkbox)').change(function(){
                 $(this).parents('tr').toggleClass('active');
            });

            // do this after .inbox-view is visible
            var ifDoc, ifRef = frame;

            // set ifDoc to 'document' from frame
            try {
                ifDoc = ifRef.contentWindow.document.documentElement;
            } catch(e1) {
                try {
                    ifDoc = ifRef.contentDocument.documentElement;
                } catch(e2) {}
            }

            // calculate and set max height for frame
            if(ifDoc) {
                var subtract_heights = [
                    $(frame).offset().top,
                    $('.footer').outerHeight(),
                ];

                var max_height = $('body').outerHeight();
                for(var height in subtract_heights) {
                    max_height = max_height - height;
                }

                if(ifDoc.scrollHeight > max_height) {
                    ifRef.height = max_height;
                } else {
                    ifRef.height = ifDoc.scrollHeight;
                }
            }
        }, 300);
    }

    // autogrow on frame load
    $(frame).load(email_frame_autogrow);

    // initialize uniform checkboxes
    App.initUniform('.mail-group-checkbox');

    // handle group checkbox toggle
    $('.mail-group-checkbox').change(function() {
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

        toggle_actions_button();
        update_bulk_ids();
    });

    // enable/disable actions button when (no) items are selected
    function toggle_actions_button() {
        var selected = $(''+$('.mail-group-checkbox').attr('data-set')+':checked');
        if(selected.length) {
            $('.mail-actions').removeClass('disabled');
            $('.email-list-archive-btn').removeClass('disabled');
        } else {
            $('.mail-actions').addClass('disabled');
            $('.email-list-archive-btn').addClass('disabled');
        }

    }
    // update forms that have actions for selected messages
    function update_bulk_ids() {
        var selected = $(''+$('.mail-group-checkbox').attr('data-set')+':not(.mail-group-checkbox):checked');
        var selected_ids = [];
        for(var i = 0; i < selected.length; i++) {
            selected_ids.push($(selected[i]).val());
        }
        $('.bulk-ids').val(selected_ids.join(','));
    }
    // on load
    toggle_actions_button();
    update_bulk_ids();

    // handle single checkbox toggle
    $('.mail-checkbox:not(.mail-group-checkbox)').change(function(){
        $(this).parents('tr').toggleClass('active');

        toggle_actions_button();
        update_bulk_ids();
    });

    // open links when clicking the reply button
    $('.reply-btn[data-href]').click(function() {
        $('.inbox-view').hide();
        $('.inbox-loading').show();
        redirect_to($(this).data('href'));
    });

    $('.search-form [type="submit"]').click(function() {
        App.blockUI($('.inbox-content'), false, '');
        $(this).button('loading');
    });
});
