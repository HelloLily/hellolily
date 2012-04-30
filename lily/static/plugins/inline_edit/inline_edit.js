/*Load jQuery if not already loaded*/
if(typeof jQuery == 'undefined'){
	document.write("<script type=\"text/javascript\" src=\"http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js\"></script>");
	var __noconflict = true;
}
//'<div class="context-loader">Saving&hellip;</div>'


(function ($){
	$(function(){
		var getEditableSelector = function(button){
			var editable_sel = $(button).attr("data-edit-selector");
			if (editable_sel == undefined){
				editable_sel = $(button).attr("href");
			}
			return editable_sel
		}
		
		// do visibility setup
		$(".iedit_form").hide();
		
		// inline edit
		$(".iedit_button").live('click', function() {
			var editable_sel = getEditableSelector(this);
			var editable = $(editable_sel).find("*").andSelf();
			duration = $(this).attr("data-edit-slide");
			
			if (duration == undefined){
			    $(".iedit_form:visible").not($(this).closest('.iedit_wrapper').find('.iedit_form')).hide();
                $(".iedit_content:not(:visible)").not($(this).closest('.iedit_wrapper').find('.iedit_content')).show();
			    
                editable.filter(".iedit_form").toggle();
				editable.filter(".iedit_content").toggle();
			}
			else {
			    duration = 150;
			    $(".iedit_form:visible").not($(this).closest('.iedit_wrapper').find('.iedit_form')).slideToggle(duration);
                content = $(".iedit_content:not(:visible)").not($(this).closest('.iedit_wrapper').find('.iedit_content'));
				
				if( content.length ) {
			         content.slideToggle(duration, function() {
                       editable.filter(".iedit_content").slideToggle(duration);
                       editable.filter(".iedit_form").slideToggle(duration);
                    });
                } else {
                   editable.filter(".iedit_content").slideToggle(duration);
                   editable.filter(".iedit_form").slideToggle(duration);  
                }
			}
			
			// check if there is a visible input to focus on
			var visibleInput = $(this).closest('.iedit_wrapper').find(':input:visible:first');
			if(visibleInput.length) {
			    setCaretAtEnd(visibleInput.get(0));
			}
            
			return false;
		});
	});
})(jQuery);