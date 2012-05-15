function enableChosen(elem) {
	/* Chosen Select Box Plugin */
	if($.fn.chosen) {
		$(elem).find("select.chzn-select:visible").chosen();
		$(elem).find("select.chzn-select-no-search:visible").chosen({disable_search_threshold: 999999});
	}
}

$(document).ready(function() {
	/* Core JS Functions */

	/* Collapsible Panels */
	$(".mws-panel.mws-collapsible.mws-collapsed .mws-panel-body").css("display", "none");
	$(".mws-panel.mws-collapsible .mws-panel-header")
		.append("<div class=\"mws-collapse-button mws-inset\"><span></span></div>")
		.find(".mws-collapse-button span")
		.live("click", function(event) {
			$(this)
				.parents(".mws-panel")
				.toggleClass("mws-collapsed")
				.find(".mws-panel-body")
				.slideToggle("fast");
		});

	/* Side dropdown menu */
	$("div#mws-navigation ul li a, div#mws-navigation ul li span")
	.bind('click', function(event) {
		if($(this).next('ul').size() !== 0) {
			$(this).next('ul').slideToggle('fast', function() {
				$(this).toggleClass('closed');
			});
			event.preventDefault();
		}
	});

	/* Responsive Layout Script */

	$("div#mws-navigation").live('click', function(event) {
		if(event.target === this) {
			$(this).toggleClass('toggled');
		}
	});

	/* Form Messages */

	$(".mws-form-message").live("click", function() {
		$(this).animate({opacity:0}, function() {
			$(this).slideUp("medium", function() {
				$(this).css("opacity", '');
			});
		});
	});

	/* Message & Notifications Dropdown */
	$("div#mws-user-tools .mws-dropdown-menu a").click(function(event) {
		$(".mws-dropdown-menu.toggled").not($(this).parent()).removeClass("toggled");
		$(this).parent().toggleClass("toggled");
		event.preventDefault();
	});

	$('html').click(function(event) {
		if($(event.target).parents('.mws-dropdown-menu').size() == 0 ) {
			$(".mws-dropdown-menu").removeClass("toggled");
		}
	});

	/* Side Menu Notification Class */
	$(".mws-nav-tooltip").addClass("mws-inset");

	/* Adding title attribute to table header, toolbar buttons and wizard navigation */
	$("table.mws-table thead tr th, .mws-panel-toolbar ul li a, .mws-panel-toolbar ul li a span, .mws-wizard ul li a, .mws-wizard ul li span").each(function() {
		$(this).attr('title', $(this).text());
	});

	/* File Input Styling */
	if($.fn.customFileInput) {
		$("input[type='file']").customFileInput();
	}

	enableChosen($('body'));

	/* Tooltips */
	if($.fn.tipsy) {
		var gravity = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'];
		for(var i in gravity)
			$(".mws-tooltip-"+gravity[i]).tipsy({gravity: gravity[i]});

		$('input[title], select[title], textarea[title]').tipsy({trigger: 'focus', gravity: 'w'});
	}

	/* Dual List Box */
	if($.configureBoxes) {
		$.configureBoxes();
	}

	/* Placeholders for browsers without support for the placeholder attribute */
	if($.fn.placeholder) {
		$('[placeholder]').placeholder();
	}

	/* Enable tabs on this class */
    $(".mws-tabs").tabs();

    /* Submit the form on ctrl + enter in any input field (including textarea/checkbox/radiobutton/select) */
    $('form.mws-form :input').live('keydown', function(event) {
    	form = $(this).closest('form');
    	submit_form_on_ctrl_enter(event, form);
    });
    
    /* Re-index tabbale elements on page load */
    if($.tabthisbody) {
        $.tabthisbody();
    }
   	
    /* Defaults for jGrowl */
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
            $(notification).dblclick(function() {
                $(this).trigger('jGrowl.beforeClose'); 
            });
        }
    };
	
});
