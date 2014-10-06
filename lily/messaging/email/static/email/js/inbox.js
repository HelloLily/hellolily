var Inbox = function () {
    var editor;

    var customParser = (function () {
        function parse(elementOrHtml, rules, context, cleanUp) {
            return elementOrHtml;
        }

        return parse;
    })();

    var initWysihtml5 = function () {
        editor = new wysihtml5.Editor("id_body_html", {
            toolbar:     "wysihtml5-toolbar",
            parser: customParser
        });

        editor.observe("load", function() {
            editor.composer.element.addEventListener("keyup", function() {
                resizeEditor();
            });
        });

        $(window).on("resize", function() {
            resizeEditor();
        });

        // Set heading properly after change
        var toolbar = $("#wysihtml5-toolbar");
        $(toolbar).find("a[data-wysihtml5-command='formatBlock']").click(function(e) {
            var target = e.target || e.srcElement;
            var el = $(target);
            $(toolbar).find(".current-font").text(el.html());
        });
    };

    var resizeEditor = function resizeEditor() {
        $(".wysihtml5-sandbox")[0].style.height = editor.composer.element.scrollHeight + "px";
    };

    var handleCCInput = function () {
        var ccLink = $(".inbox-compose .mail-to .inbox-cc");
        var inputField = $(".inbox-compose .input-cc");
        ccLink.hide();
        inputField.show();
        $(".close", inputField).click(function () {
            inputField.hide();
            ccLink.show();
            $(".input-cc").find(".tags").select2("val", "");
        });
    };

    var handleBCCInput = function () {
        var bccLink = $(".inbox-compose .mail-to .inbox-bcc");
        var inputField = $(".inbox-compose .input-bcc");
        bccLink.hide();
        inputField.show();
        $(".close", inputField).click(function () {
            inputField.hide();
            inputField.show();
            $(".input-bcc").find(".tags").select2("val", "");
        });
    };

    return {
        //main function to initiate the module
        init: function () {

            //handle compose/reply cc input toggle
            $(".inbox-compose .mail-to .inbox-cc").live("click", function () {
                handleCCInput();
            });

            //handle compose/reply bcc input toggle
            $(".inbox-compose .mail-to .inbox-bcc").live("click", function () {
                handleBCCInput();
            });

            initWysihtml5();
            App.fixContentHeight();
            App.initUniform();

        },
        getEditor: function() { return editor },
        resizeEditor: function () { resizeEditor(); }
    };

}();

$(function ($) {

    // use email-templates
    $("#id_template").change(function() {
        if(templateList) {
            var value = parseInt($(this).val());
            var subjectField = $("#id_subject");
            if (value) {
                subjectField.val(templateList[value].subject);
                Inbox.getEditor().setValue(templateList[value].html_part + "<br>" + Inbox.getEditor().getValue());
                Inbox.resizeEditor();
            } else {
                subjectField.val("");
                Inbox.getEditor().setValue("");
                Inbox.resizeEditor();
            }
        }
    });

    // open single message
    $(".inbox-content .view-message").click(function () {
        if ($(this).closest("[data-readable]").data("readable") == "False") {
            alert("Account deactivated, please activate account to view email.");
        } else {
            $(".inbox-content").hide();
            $(".inbox-loading").show();
            redirect_to($(this).closest("[data-href]").data("href"));
        }
    });

    var inboxFrame = $(".inbox-view iframe")[0];

    function emailFrameAutogrow() {
        setTimeout(function () {
            $(".inbox-loading").hide();
            $(".inbox-view").show();
            App.fixContentHeight();

            // highlight selected messages
            $(".mail-checkbox:not(.mail-group-checkbox)").change(function () {
                $(this).parents("tr").toggleClass("active");
            });

            // do this after .inbox-view is visible
            var ifDoc, ifRef = inboxFrame;

            // set ifDoc to 'document' from frame
            try {
                ifDoc = ifRef.contentWindow.document.documentElement;
            } catch (e1) {
                try {
                    ifDoc = ifRef.contentDocument.documentElement;
                } catch (e2) {
                }
            }

            // calculate and set max height for frame
            if (ifDoc) {
                var subtractHeights = [
                    $(inboxFrame).offset().top,
                    $(".footer").outerHeight()
                ];

                var maxHeight = $("body").outerHeight();
                for (var height in subtractHeights) {
                    maxHeight = maxHeight - height;
                }

                if (ifDoc.scrollHeight > maxHeight) {
                    ifRef.height = maxHeight;
                } else {
                    ifRef.height = ifDoc.scrollHeight;
                }
            }
        }, 300);
    }

    // autogrow on frame load
    $(inboxFrame).load(emailFrameAutogrow);

    // initialize uniform checkboxes
    App.initUniform(".mail-group-checkbox");

    // handle group checkbox toggle
    $(".mail-group-checkbox").change(function () {
        var set = $(this).attr("data-set");
        var checked = $(this).is(":checked");
        $(set).each(function () {
            if (checked) {
                $(this).attr("checked", true);
                $(this).parents("tr").addClass("active");
            } else {
                $(this).attr("checked", false);
                $(this).parents("tr").removeClass("active");
            }
        });
        $.uniform.update(set);

        toggleActionsButton();
        updateBulkIds();
    });

    // enable/disable actions button when (no) items are selected
    function toggleActionsButton() {
        var selected = $("" + $(".mail-group-checkbox").attr("data-set") + ":checked");
        if (selected.length) {
            $(".mail-actions").removeClass("disabled");
            $(".email-list-archive-btn").removeClass("disabled");
        } else {
            $(".mail-actions").addClass("disabled");
            $(".email-list-archive-btn").addClass("disabled");
        }

    }

    // update forms that have actions for selected messages
    function updateBulkIds() {
        var selected = $("" + $(".mail-group-checkbox").attr("data-set") + ":not(.mail-group-checkbox):checked");
        var selectedIds = [];
        for (var i = 0; i < selected.length; i++) {
            selectedIds.push($(selected[i]).val());
        }
        $(".bulk-ids").val(selectedIds.join(","));
    }

    // on load
    toggleActionsButton();
    updateBulkIds();

    // handle single checkbox toggle
    $(".mail-checkbox:not(.mail-group-checkbox)").change(function () {
        $(this).parents("tr").toggleClass("active");

        toggleActionsButton();
        updateBulkIds();
    });

    // open links when clicking the reply button
    $(".reply-btn[data-href]").click(function () {
        $(".inbox-view").hide();
        $(".inbox-loading").show();
        redirect_to($(this).data("href"));
    });

    $(".search-form [type='submit']").click(function () {
        App.blockUI($(".inbox-content"), false, "");
        $(this).button("loading");
    });

    $(".inbox-compose [type='submit']").click(function (event) {
        event.preventDefault();

        var button_name = $(this).attr('name');

        if (button_name == "submit-send") {
            // Validation of fields.
            if (!$("#id_send_to_normal").val() && !$("#id_send_to_cc").val() && !$("#id_send_to_bcc").val()) {
                $("#modal_no_email_address").modal();
                event.preventDefault();
                return;
            }
        } else if (button_name == "submit-discard") {
            // Discarding email, remove all attachments to prevent unneeded uploading.
            $("[id|=id_attachments]:file").remove();
        }

        // Make sure both buttons of the same name are set to the loading state
        $("button[name='" + button_name + "']").button("loading");
        // No validation needed, remove attachments to prevent unneeded uploading.
        App.blockUI($(".inbox-content"), false, "");
        $("[id|=id_attachments]:file").filter(function () {
            return $(this).data("formset-disabled") == true;
        }).remove();

        // Make sure form always gets submitted
        var form = $(this).closest('form');
        var form_data = $(form).serialize() + '&' + button_name;
        $.post('', form_data);
    });
});
