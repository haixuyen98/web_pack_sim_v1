window.addEventListener('load', function () {
  url_path = window.location.pathname;
  // chi chay khi vào trang chủ
  if (url_path=="/"){
    loginToken = saveMBLoginTokenParam();
    if (loginToken){
      fetch_user_info_save_local_storage(loginToken);
    }
  }

  const KEY = "mb_loginToken"
  loginToken = localStorage.getItem(KEY)
  if (loginToken){
    const zalo = document.querySelector('#zalo');
    zalo?.setAttribute('data-href', zalo.getAttribute('href'))
    zalo?.removeAttribute('href')
    zalo?.addEventListener('click', function(e) {
      e.preventDefault();
      const zaloHref = zalo.getAttribute('data-href');
      connectZalo(zaloHref);
    })

    const hotline = document.querySelector('#hotline');
    hotline?.setAttribute('data-href', hotline.getAttribute('href'))
    hotline?.removeAttribute('href')
    hotline?.addEventListener('click', function(e) {
      e.preventDefault();
      const hotlineHref = hotline.getAttribute('data-href');
      const phoneNumber = hotlineHref.replace('tel:', '');
      connectHotline(phoneNumber);
    })
    // neu tren trang co context thong tin transaction thi mo poup
    if (typeof transaction !='undefined' && transaction.status=="PENDING") {
      openModalBankingStatement()
    }
  }
});

function saveMBLoginTokenParam() {
    const KEY = "mb_loginToken"
    const loginToken_value = _getUrlParameter('loginToken')
    if (loginToken_value) {
        localStorage.setItem(KEY, loginToken_value)
        setCookie(KEY, loginToken_value, 1)
    }
    return loginToken_value
}
function fetch_user_info_save_local_storage(loginToken) {
  KEY = "mb_user"
  fetch(`/api/mb/get-user-info?loginToken=${loginToken}`)
  .then(response => response.json())
  .then(data => {
    // Process the fetched data
    if(data.code ==200 && data.user) {
      // localStorage.setItem(KEY, JSON.stringify(data.user))
      setCookie('mb_user_sessionId', data.mb_user_sessionId, 1)
      setCookie('mb_user_cif', data.mb_user_cif, 1)
      setCookie('mb_user_name', data.mb_user_name,1)
      setCookie('mb_user_phone', data.mb_user_phone,1)
    }
  })
  .catch(error => {
    console.error(error);
  });
}
function connectHotline(tel_number){
    window['ReactNativeWebView'].postMessage(JSON.stringify({
      type: 'TEL',
      data: {
        tel: tel_number
      }
    }));
}
function connectZalo(zaloHref) {
    window['ReactNativeWebView'].postMessage(JSON.stringify({
      type: 'OPEN_BROWSER',
      link: zaloHref,
    }));
}
async function openModalBankingStatement() {
  const object_send = {
    type: 'PAYMENT_HUB_TRANSACTION',
    data: {
      merchant: {
        code: merchant_code,
        name: 'Công ty Cổ phần Dịch vụ Viễn thông DTH',
      },
      type: {
        code: transaction_type,
        name: 'Mua sim số đẹp',
        allowCard: true,
      },
      id: transaction.transaction_code,
      amount: transaction.amount,
      description: transaction.description,
      successMessage: 'Cảm ơn quý khách đã mua sim số đẹp tại SimThangLong.vn. Trong 5 phút, giao dịch viên sẽ gọi lại cho quý khách'
    }
  }
  window['ReactNativeWebView'].postMessage(JSON.stringify(object_send))
}
function _getUrlParameter(name) {
    name = name.replace(/[[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}
function setCookie(name, value, hoursToExpire) {
  var expiration = new Date();
  expiration.setTime(expiration.getTime() + (hoursToExpire * 60 * 60 * 1000));
  var expires = expiration.toUTCString();

  document.cookie = `${name}=${value}; expires=${expires}; path=/`;
}

function changeSubmitType(value) {
  document.getElementById("type_submit").value = value
}