$(document).ready(function() {
	var backgroundPattern = "images/core/bg/paper.png";
	var baseColor = "#35353a";
	var highlightColor = "#c5d52b";
	var textColor = "#c5d52b";
	var textGlowColor = {r: 197, g: 213, b: 42, a: 0.5};
	
	var patterns = {
		Paper: {
			name: "Paper", 
			img: "images/core/bg/paper.png"
		}, 
		Blueprint: {
			name: "Blueprint", 
			img: "images/core/bg/blueprint.png"
		}, 
		Bricks: {
			name: "Bricks", 
			img: "images/core/bg/bricks.png"
		}, 
		Carbon: {
			name: "Carbon", 
			img: "images/core/bg/carbon.png"
		}, 
		Circuit: {
			name: "Circuit", 
			img: "images/core/bg/circuit.png"
		}, 
		Holes: {
			name: "Holes", 
			img: "images/core/bg/holes.png"
		}, 
		Mozaic: {
			name: "Mozaic", 
			img: "images/core/bg/mozaic.png"
		}, 
		Roof: {
			name: "Roof", 
			img: "images/core/bg/roof.png"
		}, 
		Stripes: {
			name: "Stripes", 
			img: "images/core/bg/stripes.png"
		}
	};
	
	var presets = {
		Default: {
			name: "Default", 
			baseColor: "35353a", 
			highlightColor: "c5d52b", 
			textColor: "c5d52b", 
			textGlowColor: {r: 197, g: 213, b: 42, a: 0.5}
		}, 
		Army: {
			name: "Army", 
			baseColor: "363d1b", 
			highlightColor: "947131", 
			textColor: "ffb575", 
			textGlowColor: {r: 237, g: 255, b: 41, a: 0.4}
		}, 
		RockyMountains: {
			name: "Rocky Mountains", 
			baseColor: "2f2f33", 
			highlightColor: "808080", 
			textColor: "b0e6ff", 
			textGlowColor: {r: 230, g: 232, b: 208, a: 0.4}
		}, 
		ChineseTemple: {
			name: "Chinese Temple", 
			baseColor: "4f1b1b", 
			highlightColor: "e8cb10", 
			textColor: "f7ff00", 
			textGlowColor: {r: 255, g: 255, b: 0, a: 0.6}
		}, 
		Boutique: {
			name: "Boutique", 
			baseColor: "292828", 
			highlightColor: "f08dcc", 
			textColor: "fcaee3", 
			textGlowColor: {r: 186, g: 9, b: 230, a: 0.5}
		}, 
		Toxic: {
			name: "Toxic", 
			baseColor: "42184a", 
			highlightColor: "97c730", 
			textColor: "b1ff4c", 
			textGlowColor: {r: 230, g: 232, b: 208, a: 0.45}
		}, 
		Aquamarine: {
			name: "Aquamarine", 
			baseColor: "192a54", 
			highlightColor: "88a9eb", 
			textColor: "8affe2", 
			textGlowColor: {r: 157, g: 224, b: 245, a: 0.5}
		}
	};
	
	var backgroundTargets = 
	[
		"body", 
		"div#mws-container"
	];
	
	var baseColorTargets = 
	[
		"div#mws-sidebar-bg", 
	 	"div#mws-header", 
		".mws-panel .mws-panel-header", 
		"div#mws-error-container", 
		"div#mws-login", 
		"div#mws-login .mws-login-lock", 
		".ui-accordion .ui-accordion-header", 
		".ui-tabs .ui-tabs-nav", 
		".ui-datepicker", 
		".fc-event-skin", 
		".ui-dialog .ui-dialog-titlebar", 
		"div.jGrowl div.jGrowl-notification, div.jGrowl div.jGrowl-closer", 
		"div#mws-user-tools .mws-dropdown-menu .mws-dropdown-box", 
		"div#mws-user-tools .mws-dropdown-menu.toggled a.mws-dropdown-trigger"
	];
	
	var borderColorTargets = 
	[
	 	"div#mws-header"
	];
	
	var highlightColorTargets = 
	[
		"div#mws-searchbox input.mws-search-submit", 
		".mws-panel .mws-panel-header .mws-collapse-button span", 
		"div.dataTables_wrapper .dataTables_paginate div", 
		"div.dataTables_wrapper .dataTables_paginate span.paginate_active", 
		".mws-table tbody tr.odd:hover td", 
		".mws-table tbody tr.even:hover td", 
		".fc-state-highlight", 
		".ui-slider-horizontal .ui-slider-range", 
		".ui-slider-vertical .ui-slider-range", 
		".ui-progressbar .ui-progressbar-value", 
		".ui-datepicker td.ui-datepicker-current-day", 
		".ui-datepicker .ui-datepicker-prev .ui-icon", 
		".ui-datepicker .ui-datepicker-next .ui-icon", 
		".ui-accordion-header .ui-icon", 
		".ui-dialog-titlebar-close .ui-icon"
	];
	
	var textTargets = 
	[
		".mws-panel .mws-panel-header span", 
		"div#mws-navigation ul li.active a", 
		"div#mws-navigation ul li.active span", 
		"div#mws-user-tools #mws-username", 
		"div#mws-navigation ul li span.mws-nav-tooltip", 
		"div#mws-user-tools #mws-user-info #mws-user-functions #mws-username", 
		".ui-dialog .ui-dialog-title", 
		".ui-state-default", 
		".ui-state-active", 
		".ui-state-hover", 
		".ui-state-focus", 
		".ui-state-default a", 
		".ui-state-active a", 
		".ui-state-hover a", 
		".ui-state-focus a"
	];
	
	$("#mws-themer-getcss").bind("click", function(event) {
		$("#mws-themer-css-dialog textarea").val(generateCSS("../"));
		$("#mws-themer-css-dialog").dialog("open");
		event.preventDefault();
	});
	
	var presetDd = $('<select id="mws-theme-presets"></select>');
	for(var i in presets) {
		var option = $("<option></option>").text(presets[i].name).val(i);
		presetDd.append(option);
	}
	$("#mws-theme-presets-container").append(presetDd);
	
	presetDd.bind('change', function(event) {
		updateBaseColor(presets[presetDd.val()].baseColor);
		updateHighlightColor(presets[presetDd.val()].highlightColor);
		updateTextColor(presets[presetDd.val()].textColor);
		
		updateTextGlowColor(presets[presetDd.val()].textGlowColor, presets[presetDd.val()].textGlowColor.a);
		
		attachStylesheet();
		
		event.preventDefault();
	});
	
	
	var patternDd = $('<select id="mws-theme-patterns"></select>');
	for(var i in patterns) {
		var option = $("<option></option>").text(patterns[i].name).val(i);
		patternDd.append(option);
	}
	$("#mws-theme-pattern-container").append(patternDd);
	
	patternDd.bind('change', function(event) {
		updateBackground(patterns[patternDd.val()].img, true);
		
		event.preventDefault();
	});
	
	$("div#mws-themer #mws-themer-toggle").bind("click", function(event) {
		if($(this).hasClass("opened")) {
			$(this).toggleClass("opened").parent().animate({right: "0"}, "slow");
		} else {
			$(this).toggleClass("opened").parent().animate({right: "256"}, "slow");
		}
	});
	
	$("div#mws-themer #mws-textglow-op").slider({
		range: "min", 
		min:0, 
		max: 100, 
		value: 50, 
		slide: function(event, ui) {
			alpha = ui.value * 1.0 / 100.0;
			updateTextGlowColor(null, alpha);
		}
	});
	
	$("div#mws-themer #mws-themer-css-dialog").dialog({
		autoOpen: false, 
		title: "Theme CSS", 
		width: 500, 
		modal: true, 
		resize: false, 
		buttons: {
			"Close": function() { $(this).dialog("close"); }
		}
	});
	
	$("#mws-base-cp").ColorPicker({
		color: baseColor, 
		onShow: function (colpkr) {
				$(colpkr).fadeIn(500);
				return false;
		},
		onHide: function (colpkr) {
				$(colpkr).fadeOut(500);
				return false;
		},
		onChange: function (hsb, hex, rgb) {			
			updateBaseColor(hex, true);
		}
	});
	
	$("#mws-highlight-cp").ColorPicker({
		color: highlightColor, 
		onShow: function (colpkr) {
				$(colpkr).fadeIn(500);
				return false;
		},
		onHide: function (colpkr) {
				$(colpkr).fadeOut(500);
				return false;
		},
		onChange: function (hsb, hex, rgb) {			
			updateHighlightColor(hex, true);
		}
	});
	
	$("#mws-text-cp").ColorPicker({
		color: textColor, 
		onShow: function (colpkr) {
				$(colpkr).fadeIn(500);
				return false;
		},
		onHide: function (colpkr) {
				$(colpkr).fadeOut(500);
				return false;
		},
		onChange: function (hsb, hex, rgb) {			
			updateTextColor(hex, true);
		}
	});
	
	$("#mws-textglow-cp").ColorPicker({
		color: textGlowColor, 
		onShow: function (colpkr) {
				$(colpkr).fadeIn(500);
				return false;
		},
		onHide: function (colpkr) {
				$(colpkr).fadeOut(500);
				return false;
		},
		onChange: function (hsb, hex, rgb) {
			updateTextGlowColor(rgb, textGlowColor["a"], true);
		}
	});
	
	function updateBackground(bg, attach)
	{
		backgroundPattern = bg;
		
		if(attach == true)
			attachStylesheet();
	}
	
	function updateBaseColor(hex, attach)
	{
		baseColor = "#" + hex;
		$("#mws-base-cp").css('backgroundColor', baseColor);
		
		if(attach === true)
			attachStylesheet();
	}
	
	function updateHighlightColor(hex, attach)
	{
		highlightColor = "#" + hex;
		$("#mws-highlight-cp").css('backgroundColor', highlightColor);
		
		if(attach === true)
			attachStylesheet();
	}
	
	function updateTextColor(hex, attach)
	{
		textColor = "#" + hex;
		$("#mws-text-cp").css('backgroundColor', textColor);
		
		if(attach === true)
			attachStylesheet();
	}
	
	function updateTextGlowColor(rgb, alpha, attach)
	{
		if(rgb != null) {
			textGlowColor.r = rgb["r"];
			textGlowColor.g = rgb["g"];
			textGlowColor.b = rgb["b"];
			textGlowColor.a = alpha;
		} else {
			textGlowColor.a = alpha;
		}
		
		$("div#mws-themer #mws-textglow-op").slider("value", textGlowColor.a * 100);
		$("#mws-textglow-cp").css('backgroundColor', '#' + rgbToHex(textGlowColor.r, textGlowColor.g, textGlowColor.b));
		
		if(attach === true)
			attachStylesheet();
	}
	
	function attachStylesheet(basePath)
	{
		if($("#mws-stylesheet-holder").size() == 0) {
			$('body').append('<div id="mws-stylesheet-holder"></div>');
		}
		
		$("#mws-stylesheet-holder").html($('<style type="text/css">' + generateCSS(basePath) + '</style>'));
	}
	
	function generateCSS(basePath)
	{
		if(!basePath)
			basePath = "";
			
		var css = 
			backgroundTargets.join(", \n") + "\n" + 
			"{\n"+
			"	background-image:url('" + basePath + backgroundPattern + "');\n"+
			"}\n\n"+			
			baseColorTargets.join(", \n") + "\n" + 
			"{\n"+
			"	background-color:" + baseColor + ";\n"+
			"}\n\n"+
			borderColorTargets.join(", \n") + "\n" + 
			"{\n"+
			"	border-color:" + highlightColor + ";\n"+
			"}\n\n"+
			textTargets.join(", \n") + "\n" + 
			"{\n"+
			"	color:" + textColor + ";\n"+
			"	text-shadow:0 0 6px rgba(" + getTextGlowArray().join(", ") + ");\n"+
			"}\n\n"+
			highlightColorTargets.join(", \n") + "\n" + 
			"{\n"+
			"	background-color:" + highlightColor + ";\n"+
			"}\n";
			
		return css;
	}
	
	function getTextGlowArray()
	{
		var array = new Array();
		for(var i in textGlowColor)
			array.push(textGlowColor[i]);
			
		return array;
	}
	
	function rgbToHex(r, g, b)
	{
		var rgb = b | (g << 8) | (r << 16);
		return rgb.toString(16);
	}
});