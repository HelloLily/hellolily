$(document).ready(function() {
	// TODO: put in utils or something    
    $('input:checkbox').screwDefaultButtons({
        checked:    'url(/static/plugins/screwdefaultbuttons/images/checkbox_checked.png)',
        unchecked:  'url(/static/plugins/screwdefaultbuttons/images/checkbox_unchecked.png)',
        width:      16,
        height:     16
    }); 
});