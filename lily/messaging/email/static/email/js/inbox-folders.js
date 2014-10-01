$(function($) {
    /**
     * Highlight item from event, and remove highlighting from others.
     */
    function select_tree_item(event) {
        // find current item and other items
        var item = event.currentTarget;
        var all = $(item).closest('.tree').find('.tree-selected');

        // remove highlighting
        if(all.length && $(all)[0] !== $(item)[0]) {
            all.removeClass('tree-selected');
        }

        // toggle highlighting
        if($(item).hasClass('tree-selected')) {
            $(item).removeClass('tree-selected');
        } else {
            $(item).addClass ('tree-selected');
        }
    }

    /**
     * Toggles visibility for folder from event and hides all other
     * folders' content.
     */
    function select_tree_folder(event) {
        // find current folder and content
        var folder = event.currentTarget;
        var folder_content = $(folder).next('.tree-folder-content:first');
        if($(folder).next('.slimScrollDiv:first').length) {
            folder_content = $(folder).next('.slimScrollDiv:first');
        }

        // toggle visibility
        if($(folder).find('.icon-folder-close').length) {
            $(folder).find('.icon-folder-close').addClass('icon-folder-open').removeClass('icon-folder-close');
            $(folder_content).removeClass('hide').show();
            if($(folder_content).data('scroller')) {
                var height;
                if ($(folder_content).attr("data-height")) {
                    height = $(folder_content).attr("data-height");
                } else {
                    height = $(folder_content).css('height');
                }
                $(folder_content).slimScroll({
                    size: '7px',
                    color: ($(folder_content).attr("data-handle-color")  ? $(folder_content).attr("data-handle-color") : '#a1b2bd'),
                    railColor: ($(folder_content).attr("data-rail-color")  ? $(folder_content).attr("data-rail-color") : '#333'),
                    position: 'right',
                    height: height,
                    alwaysVisible: ($(folder_content).attr("data-always-visible") == "1" ? true : false),
                    railVisible: ($(folder_content).attr("data-rail-visible") == "1" ? true : false),
                    disableFadeOut: true
                });
                $(folder_content).data('scroller', false);
            }

            // triger toggle for others
            $(folder).closest('.tree').find('.tree-folder-header').trigger('selected', folder);
        } else {
            $(folder).find('.icon-folder-open').addClass('icon-folder-close').removeClass('icon-folder-open');
            $(folder_content).hide();
        }
    }

    /**
     * Hides folder content for folder from event if it's not a parent of *folder*.
     */
    function collapse_folder_content(event, folder) {
        // do not collapse *folder*
        if(event.currentTarget != folder) {
            // do not collapse parents of *folder*
            var folder_content = $(event.currentTarget).next('.tree-folder-content:first');
            if($(event.currentTarget).next('.slimScrollDiv:first').length) {
                folder_content = $(event.currentTarget).next('.slimScrollDiv:first');
            }

            var is_parent = $(folder_content).find('.tree-folder-header').filter(function(index, element) {
                return element == folder;
            }).length > 0;
            if(!is_parent) {
                // hide folder content
                if($(event.currentTarget).find('.icon-folder-open').length) {
                    $(event.currentTarget).find('.icon-folder-open').addClass('icon-folder-close').removeClass('icon-folder-open');
                    $(folder_content).hide();
                }
            }
        }
    }

    // bind on click
    $('.mailbox-folders.tree .tree-folder-header').click(select_tree_folder);

    // bind custom event
    $('.mailbox-folders.tree .tree-folder-header').bind('selected', collapse_folder_content);

    // open links when clicking the tree item/folder
    $('.tree-folder-header[data-href], .tree-item[data-href]').click(function() {
        $('.inbox-view').hide();
        $('.inbox-loading').show();
        redirect_to($(this).data('href'));
    });
});
