

const REMOVE_TWO_STAR = /([\*])\1+/;
const HEADS = ['086', '089', '088', '092', '099', '087', '024', '055', '096', '090', '091', 
  '056', '059', '097', '093', '094', '058', '098', '070', '083', '032', '079', '084', '033', 
  '077', '085', '034', '076', '081', '035', '078', '082', '036', '037', '038', '039'];

document.addEventListener('DOMContentLoaded', function () {
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  const q = urlParams.get('q')
  document.getElementById("nav-search").value = q;
});


function handleSearchSubmit() {
  var keyword = document.getElementById("nav-search").value;
  var regex = /^\d{10,11}$/;
  var isValidPhoneNumber = regex.test(keyword);
  if (isValidPhoneNumber) {
    var baseUrl = window.location.protocol + "//" + window.location.host;
    window.location.href=`${baseUrl}/${keyword}`;
    return false;
  }
  window.location.href = `/${keywordToURLPath(keyword)}`;
  return false;
}

function handleSearchChange(e) {
  let valueConvert = e.value;
  e.value = valueConvert.replace(/[^0-9\*]/g, "");
};

function getUrlByKeyWord(keyword) {
  if ([10, 11].includes(keyword.trim().length) && !keyword.includes("*")) {
    return `${keyword}`;
  }

  let keywordTemp = keyword;
  let hasStar = false;
  if (keywordTemp[0] == "*") {
    hasStar = true;
  }
  if (keywordTemp[keywordTemp.length - 1] == "*") {
    hasStar = true;
  }
  const arr = removeDuplicateStar(keyword).split('*')
  let url = ``
  if (arr.length == 1 && keyword.length > 0) {
    // check neu
    url = searchSingle(keyword)
  } else if (arr.length == 2) {
    if (arr[0] && arr[1]) {
      url = getSearchNicePath(arr[1]);
      if (url.length > 0) {
        url = `${url}-dau-${arr[0]}`
      } else {
        url += `sim-so-dep-duoi-${arr[1]}-dau-${arr[0]}`
      }
    } else if (arr[0]) {
      url += `sim-dau-so-${arr[0]}`
    } else if (arr[1]) {
      url = searchSingle(keyword)
    }
  } else if (arr.length >= 3) {
    if (arr[0] == "" && arr[2] == "") {
      url += `sim-so-dep-${arr[1]}-giua`

    } else if (arr[0] == "") {
      url = getSearchNicePath(arr[2]);
      if (url.length > 0) {
        url = `${url}-dau-${arr[1]}`
      } else {
        url += `sim-so-dep-duoi-${arr[2]}-giua-${arr[1]}`
      }
    } else if (arr[2] == "") {
      url += `sim-so-dep-dau-${arr[0]}-giua-${arr[1]}`
    } else {
      url += `sim-so-dep-dau-${arr[0]}-giua-${arr[1]}-duoi-${arr[2]}`
    }
  }
  if (!url.includes('dau-so')) {
    keyword = `${!hasStar && arr.length == 1 ? "*" : ""}${keyword}`
  } else {
    keyword = `${keyword}${!hasStar && arr.length == 1 ? "*" : ""}`
  }
  return url
}

function keywordToURLPath(keyword) {
  let url = getUrlByKeyWord(keyword)
  // neu co dau ? truoc thi them dau &
  // if (url.includes("?")) {
  //   url = `${url}&q=${keyword}`
  // } else {
  //   url = `${url}?q=${keyword}`
  // }
  return url
}

function searchSingle(keyword) {
  if (keyword[0] === "*" && keyword[keyword.length - 1] == "*") {
    return `sim-so-dep-${keyword.replaceAll("*", "")}-giua`
  }
  else if (keyword[0] === "*") {
    return searchSingleNice(keyword)
  } else if (keyword[keyword.length - 1] == "*") {
    return `sim-dau-so-${keyword.replace("*", "")}`
  } else {
    if (keyword >= 1950 && keyword <= 2024) {
      return `sim-nam-sinh-${keyword.replaceAll("*", "")}`
    } else {
      return searchSingleNice(keyword)
    }
  }
}

function searchSingleNice(keyword) {
  let keywordTemp = keyword.replaceAll("*", "")
  let url = getSearchNicePath(keywordTemp)
  if (keywordTemp[0] !== "0" && url.length > 0) {
    return url;
  } else {
    // kiem tra keyword co phai la dau so
    const itemTel = HEADS.find((item) => {
      if (item.includes(keywordTemp)) {
        return true;
      }
    })
    if (itemTel && keyword[0] != "*") {
      if(keyword.length > 1)
      {
        return `sim-dau-so-${keywordTemp}`
      } else {
        return `sim-so-dep-duoi-${keywordTemp}`
      }
    } else if (keyword[0] == "*") {
      return `sim-so-dep-duoi-${keywordTemp}`
    }
    return `sim-so-dep-duoi-${keywordTemp}`;
  }
}

function getSearchNicePath(keyword) {
  const sameDigit = checkSameDigits(keyword);
  if (sameDigit && `${parseInt(keyword)}`.length >= 2) {
    const numLength = keyword.length;
    if (numLength == 3) {
      return `sim-tam-hoa-${keyword}`
    } else if (numLength == 4) {
      return `sim-tu-quy-${keyword}`
    } else if (numLength == 5) {
      return `sim-ngu-quy-${keyword}`
    } else if (numLength == 6) {
      return `sim-luc-quy-${keyword}`
    }
  }
  if ("0123456789".includes(keyword) && keyword.length >= 3) {
    return `sim-tien-len-duoi-${keyword}`
  }
  return ""
}

function checkSameDigits(N) {
  // Find the last digit
  var digit = N % 10;
  while (N != 0) {
    // Find the current last digit
    var current_digit = N % 10;
    // Update the value of N
    N = parseInt(`${N / 10}`);
    // If there exists any distinct
    // digit, then return No
    if (current_digit != digit) {
      return false;
    }
  }
  // Otherwise, return Yes
  return true;
}
function removeDuplicateStar(keyword) {
  return keyword.replace(REMOVE_TWO_STAR, '*')
}
