var currentCustomizePriceEditItem = null;

function addCustomizePrice(__this) {
  $('.header-modal-customize').text('Thêm mới tuỳ chỉnh giá');
  $('.fm-customize').find('input[name="price_from"]').val('');
  $('.fm-customize').find('input[name="price_to"]').val('');
  $('.fm-customize').find('input[name="percent"]').val('');
  $('.fm-customize').find('select[name="rounding"]').val('10').change();
  $('#customize-modal').modal('show');
}
function saveCustomizePrice(e){
  e.preventDefault();
  var price_from_val = $('.fm-customize').find('input[name="price_from"]').val();
  var price_to_val = $('.fm-customize').find('input[name="price_to"]').val();
  var percent_val = $('.fm-customize').find('input[name="percent"]').val();

  var price_from = parseInt(price_from_val.replace(/([^0-9])/g,""));
  var price_to = parseInt(price_to_val.replace(/([^0-9])/g,""));
  var percent = Number($('.fm-customize').find('input[name="percent"]').val());
  var data = getCustomizeJson();
  let price_error;
  const resSearchCustomize = data.filter(item => item.price_from == price_from && item.price_to == price_to).length
  if(price_from_val == ''){
    alert("Vui lòng điền mức giá từ");
    $('.fm-customize').find('input[name="price_from"]').focus();
    $('.fm-customize').find('input[name="price_from"]').css({"color":"red", "border":"1px solid red"});
    return false;
  } 
  if(price_to_val == ''){
    alert("Vui lòng điền mức giá đến");
    $('.fm-customize').find('input[name="price_to"]').focus();
    $('.fm-customize').find('input[name="price_to"]').css({"color":"red", "border":"1px solid red"});
    return false;
  }
  if(percent_val == ''){
    alert("Vui lòng điền phần trăm điều chỉnh giá");
    $('.fm-customize').find('input[name="percent"]').focus();
    $('.fm-customize').find('input[name="percent"]').css({"color":"red", "border":"1px solid red"});
    return false;
  }
  if(percent > 100){
    alert('Dữ liệu vượt quá giới hạn 100%, Vui lòng nhập lại!');
    return false;
  }
  if (Number(price_from) >= Number(price_to)){
    price_error = true;
    alert('Mức "giá từ" không được cao hơn hoặc bằng "giá đến"');
    return false;
  } else {
    price_error = false;
  }
  if (currentCustomizePriceEditItem == null) {
    if(price_from_val && price_to_val && resSearchCustomize){
      price_error = true;
      alert('Giá trị đã tồn tại, vui lòng nhập lại')
      return false;
    } else {
      price_error = false;
    }
    if(!price_error && price_from && price_to && !resSearchCustomize){
      for(let i=0; i< data.length; i++){
        if((data[i].price_from < price_from && data[i].price_to > price_from) || (data[i].price_from < price_to && data[i].price_to > price_to) || (data[i].price_from > price_from && data[i].price_to < price_to)){
          price_error = true;
          alert(`Điều chỉnh thất bại!! Đã tồn tại điều chỉnh giá từ ${data[i].price_from}đ đến ${data[i].price_to}đ, vui lòng kiểm tra lại điều kiện`)
          return false;
        } else {
          price_error = false;
        }
      }
    }
  } else {
    if(price_from_val && price_to_val && resSearchCustomize > 1){
      alert('Giá trị đã tồn tại, vui lòng nhập lại')
      return;
    } 
  }

  if(price_from !== null && price_to !== null && !price_error && percent <= 100){
    $('#changelist-form').submit();
  }
}

function editCustomizePrice(__this){
  $('.header-modal-customize').text('Sửa tuỳ chỉnh giá');
  currentCustomizePriceEditItem = __this.closest('.item-customize-price');
  var edit_price_from = currentCustomizePriceEditItem.attr('data-price-from').replace(/\B(?=(\d{3})+(?!\d)\.?)/g, ".");
  var edit_price_to = currentCustomizePriceEditItem.attr('data-price-to').replace(/\B(?=(\d{3})+(?!\d)\.?)/g, ".");
  $('.fm-customize').find('input[name="price_from"]').val(edit_price_from);
  $('.fm-customize').find('input[name="uuid"]').val(currentCustomizePriceEditItem.attr('data-uuid'));
  $('.fm-customize').find('input[name="price_to"]').val(edit_price_to);
  $('.fm-customize').find('input[name="percent"]').val(currentCustomizePriceEditItem.attr('data-percent'));
  $('.fm-customize').find('select[name="rounding"]').val(currentCustomizePriceEditItem.attr('data-rounding')).change();
  $('#customize-modal').modal('show');
}

function deleteCustomizePrice(__this){
  currentCustomizePriceEditItem = __this.closest('.item-customize-price');
  $('#id_del_uuid').val(currentCustomizePriceEditItem.attr('data-uuid'));
  $('#changelist-form').submit()
}

function getCustomizeJson() {
  var dataResponse = [];
  var element = $('#tbl-customize-price .item-customize-price');
  $(element).parent().find('.item-customize-price').each(function () {
    var json = { 
      price_from: $(this).attr('data-price-from'),
      price_to: $(this).attr('data-price-to'),
      percent: $(this).attr('data-percent'),
    }
    dataResponse.push(json);
  });
  return dataResponse;
}

$('.fm-customize').find('input[name="price_from"]').on('change click keyup input paste',(function (event) {
  $(this).css({"color": "#333", "border": "1px solid #ccc"});
  if(event.which >= 37 && event.which <= 40){
    event.preventDefault();
  }
  $(this).val(function(index, value) {
      return value
      .replace(/\D/g, "")
      .replace(/\B(?=(\d{3})+(?!\d)\.?)/g, ".");
  });
}));

$('.fm-customize').find('input[name="price_to"]').on('change click keyup input paste',(function (event) {
  $(this).css({"color": "#333", "border": "1px solid #ccc"});
  if(event.which >= 37 && event.which <= 40){
    event.preventDefault();
  }
  $(this).val(function(index, value) {
      return value
      .replace(/\D/g, "")
      .replace(/\B(?=(\d{3})+(?!\d)\.?)/g, ".");
  });
}));

$('input[name="percent"]').keyup(function() {
  var field = $(this).closest('.fm-customize__item').find('input[name="percent"]');
  var percent = Number(field.val())
  if(percent > 100){
    alert('Dữ liệu vượt quá giới hạn 100%, Vui lòng nhập lại!')
  }
});