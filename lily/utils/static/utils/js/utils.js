/* Call focus on an element with given id if found in the DOM */
function set_focus(id) {
   element = document.getElementById(id);
   if(element) {
       element.focus();
   }
}