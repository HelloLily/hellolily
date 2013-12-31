$(function($) {
    var iframe = $('#id_body_html').nextAll('.wysihtml5-sandbox').eq(0);
    var last_focussed_body_part = null;

    function insertTextAtCursor(text) {
        if(!text) return;

        var range, caretIndex, firstNode, textOffset, lastNode, firstParentNode, lastParentNode, firstNodeText, lastNodeText, caretNode;

        if(!last_focussed_body_part) {
            last_focussed_body_part = iframe;
            $(iframe).focus().blur();
        }
        var el = last_focussed_body_part.get(0);

        // get the selection from the iframe
        var sel = rangy.getIframeSelection(el);

        // default selection case: selection starting at the left side of the selected text
        firstNode = sel.anchorNode;
        lastNode = sel.focusNode;
        textOffset = sel.anchorOffset;

        if(sel.isBackwards()) {
            // swap first/last node
            firstNode = sel.focusNode;
            lastNode = sel.anchorNode;
            textOffset = sel.focusOffset;
        }

        firstNode = firstNode || $(iframe).contents().find('body').get(0);
        lastNode = lastNode || $(iframe).contents().find('body').get(0);

        // we need to wrap the parentNode in jquery because the nodes themself are just text instead of elems

        // delete selected text from the document because we're replacing this selection
        sel.deleteFromDocument();

        // also the parentNode is the node itself when it has no data so we don't need to get parent in that case

        // find element that contains the start of the selection (firstNode can be plain text or an element)
        if(firstNode.data) {
            // firstNode is plain text
            firstParentNode = $(firstNode.parentNode);
        } else {
            // firstNode is an element
            firstParentNode = $(firstNode);
        }

        // find element that contains the end of the selection (lastNode can be plain text or an element)
        if(lastNode.data) {
            // lastNode is plain text
            lastParentNode = $(lastNode.parentNode);
        } else {
            // lastNode is an element
            lastParentNode = $(lastNode);
        }

        // get text from nodes without the selected text (this was just deleted)
        firstNodeText = firstNode.data || '';
        lastNodeText = lastNode.data || '';

        if(firstNode == lastNode) {
            // if selection start and end is in the same node, simply slice text

            var beforeSelectedText = firstNodeText.slice(0, textOffset);
            var afterSelectedText = lastNodeText.slice(textOffset);
            // set new text
            $(firstParentNode).html(beforeSelectedText + text + afterSelectedText);
        } else {
            // if selection start and end are in different nodes

            if($.inArray(firstNode.parentNode, lastNode.parentNode.childNodes) !== -1) {
                // lastNode is not a child of firstNode, but the parent

                // move the text from lastNode to firstParentNode
                $(firstParentNode).append(text + lastNodeText);

                // remove lastNodeText from lastParentNode
                $(lastParentNode).html($(lastParentNode).html().substring(0, ($(lastParentNode).html().length - lastNodeText.length)));
            } else if($.inArray(lastNode.parentNode, firstNode.parentNode.childNodes) !== -1) {
                // firstNode is not a child of lastNode, but the parent

                var beforeSelectedText = firstNodeText.slice(0, textOffset);
                var afterSelectedText = lastNodeText + firstNodeText.substring(textOffset);

                // move the text from lastNodeText to firstParentNode
                $(firstParentNode).html(beforeSelectedText + text + afterSelectedText);

                // remove (the text from) lastParentNode
                $(lastParentNode).remove();

            } else {
                // firstNode and lastNode are not parentNode/childNode of each other

                // move the text from lastParentNode to firstParentNode
                $(firstParentNode).append(text + $(lastParentNode).html());

                // remove (the text from) lastParentNode
                $(lastParentNode).remove();
            }
        }

        // create a new range and refresh the selection after DOM manipulation
        range = rangy.createRange($(iframe).contents()[0]);
        sel.refresh();

        // set carent behind text, which is always in firstParentNode
        caretIndex = textOffset + text.length;

        // find the index in the firstParentNode childNodes
        $.each($(firstParentNode).get(0).childNodes, function(index, node) {
            if(node.data) {
                if(caretIndex > node.data.length) {
                    caretIndex -= node.data.length;
                } else {
                    caretNode = node;
                }
            }
        });

        range.setStart(caretNode, caretIndex);
        range.setEnd(caretNode, caretIndex);

        // remove old ranges and add the new one, this places the caret at the specified index
        sel.removeAllRanges();
        sel.addRange(range);
    }

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
        insertTextAtCursor(textvalue);

        event.preventDefault();
    });

    $('#body_file_upload').click(function(event) {
        $('#id_body_file').click();

        event.preventDefault();
    });
});
