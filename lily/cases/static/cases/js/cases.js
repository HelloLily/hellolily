$(document).ready(function() {
	// reset account/contact selection if one of them has a valid value
	$('.contact_account').each(function(index, select) {
		$(select).live('change', function() {
			var elements = $(this).closest('.mws-form-row').find('.contact_account');
			var sibling = $(elements).filter(function(index, element) { return select != element; });
			
			if( $(select).val() != '' && sibling.length) {
        		sibling[0].selectedIndex = 0;
        		$(sibling[0]).trigger('liszt:updated');
			}
		});
	});
	
	// show priority icons in the select element
	var prio_classes = ['', 'green', 'yellow', 'orange', 'red'];
	$('.priority-select').each(function(index, element) {
		$(element).next('.chzn-container').find('.chzn-single').addClass('i-16 i-tag').addClass(prio_classes[$(element)[0].selectedIndex]);
	});
	$('.priority-select').live('change', function() {
		for(var i =0; i < prio_classes.length; i++) {
			$(this).next('.chzn-container').find('.chzn-single').removeClass(prio_classes[i]);
		}
		$(this).next('.chzn-container').find('.chzn-single').addClass(prio_classes[$(this)[0].selectedIndex]);
	});
});