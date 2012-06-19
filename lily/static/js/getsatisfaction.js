// Based on https://getsatisfaction.com/devcommunity/topics/asynchronously_load_the_widget?utm_medium=widget&utm_source=widget_devcommunity

// callback function to instantiate the tab when the JS loads 
var loadGsTab = function() 
{ 
    //create a container div for the widget to load into 
    var gsdiv = document.createElement('div'); 
    gsdiv.id = "gs-widget"; 
    document.body.appendChild(gsdiv); 

    var feedback_widget_options = {}; 
    
    feedback_widget_options.display = "overlay";  
    feedback_widget_options.company = "hellolily";
    feedback_widget_options.placement = "left";
    feedback_widget_options.color = "#1c76bc";
    feedback_widget_options.style = "idea";

    //this line is not in your options by default so it must be added for this to work 
    feedback_widget_options.container = "gs-widget"; 

    var feedback_widget = new GSFN.feedback_widget(feedback_widget_options); 
} 

$(document).ready(function() {
    //asynchronously load the GetSatisfaction widget 
    var gs = document.createElement('script'); 
    gs.type = 'text/javascript'; 
    gs.async = true; 
    gs.src = ('https:' == document.location.protocol ? 'https' : 'http') + '://d3rdqalhjaisuu.cloudfront.net/javascripts/feedback-v2.js'; 
    gs.onload = gs.onreadystatechange = loadGsTab;
    
    //insert before first script tag 
    var fs = document.getElementsByTagName('script')[0]; 
    fs.parentNode.insertBefore(gs, fs); 
});