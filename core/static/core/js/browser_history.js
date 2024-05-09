window.addEventListener('load', function() {
  // Get the current link
  var currentLink = window.location.href;
  saveHistoryBrowsers(currentLink);
});

function saveHistoryBrowsers (link) {
  const MAX_HISTORY_BROWSERS = 40
  const LINK_HISTORY_BROWSER = "browser_history"
  if(link){
    let arr = getBrowserHistory(LINK_HISTORY_BROWSER)
    const filterItem = arr.filter(
      (item) => item == link
    )
    if (filterItem.length === 0) {
      arr.unshift(link) //insert to first
      if (arr.length > MAX_HISTORY_BROWSERS) {
        arr = arr.slice(0, MAX_HISTORY_BROWSERS)
      }
      localStorage.setItem(LINK_HISTORY_BROWSER, JSON.stringify(arr))
    }
  }
}
function getBrowserHistory (key) {
    let item = localStorage.getItem(key)
    let arr = JSON.parse(item) || []
    return arr
}