window.addEventListener('load',function() {
    var els = document.getElementsByClassName("item_menu_check"); 
    // loops els
    for(var i = 0, x = els.length; i < x; i++) {
        els[i].onclick = function(e){
            menuItemClick(e)
        }
    }
})
function menuItemClick(e) {
    panelId = e.currentTarget.getAttribute("data-id");
    el = document.getElementById(panelId);
    el.classList.add('theme-editor__panel--is-visible')
    el.classList.add('theme-editor__panel--is-active')
}
function closeSection(panelId) {
    el = document.getElementById(panelId);
    el.classList.remove('theme-editor__panel--is-visible')
    el.classList.remove('theme-editor__panel--is-active')
}