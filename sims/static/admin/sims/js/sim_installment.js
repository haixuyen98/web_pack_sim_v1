document.addEventListener("DOMContentLoaded", function() {
  //công nợ kh
  var order_type = $("[name='id_order_type']").val(); //Loại đơn
  var store_type = $("[name='id_store_type']").val(); //Kho
  var installment = 4; //Đơn trả góp
  var common = 1; //Đơn thường
  var kho_sim = 3; //Kho SIM
  var kho_appsim = 2; //Kho App Sim;
  var percent = 1; //% / tháng
  if(order_type == common){
    $('#accountreceivable_set-empty').after(
      '<tr>' +
          '<td></td>' +
          '<td>Tổng cộng</td>' +
          '<td></td>' +
          '<td></td>' +
          '<td class="sum_amount_customer" style="text-align: center;"></td>' +
          '<td class="sum_remain_customer" style="text-align: center;"></td>' +
          '<td></td>' +
          '<td></td>' +
          '<td></td>' +
          '<td></td>' +
          '<td></td>' +
      '</tr>'
    )
  } else {
    $('#accountreceivable_set-empty').after(
      '<tr>' +
          '<td></td>' +
          '<td>Tổng cộng</td>' +
          '<td></td>' +
          '<td></td>' +
          '<td class="sum_amount_customer" style="text-align: center;"></td>' +
          '<td class="sum_interest"></td>' +
          '<td class="sum_remain_customer" style="text-align: center;"></td>' +
          '<td class="sum_interest_temp"></td>' +
          '<td></td>' +
          '<td></td>' +
          '<td></td>' +
          '<td></td>' +
      '</tr>'
    )
  }
  $(document).ready(function() {
    //tính tổng
    sum_amount_payment('')

    //set action readonly status money
    $(`.dynamic-accountreceivable_set`).find(`select[name^='accountreceivable_set'][name$='status']`).each(function(){
      var col_index = $(this).closest('tbody').find(`select[name^='accountreceivable_set'][name$='status']`).index(this);
      var col_value = $(this).val();
      disable_column_data('', col_index, col_value);
    })
    $('#accountreceivable_set-group').addClass('ov-flow');
    $('#accountreceivable_set-2-group').addClass('ov-flow');

    $('#accountreceivable_set-group').find('.add-row td').append('<span class="add-debt">Thêm một Công nợ KH </span>');
    var money_sim = $("[name='amount']").val();
    var amount_payment = sum_Column_Amount('', '.field-amount_payment');
    if(Number(amount_payment)>=Number(money_sim) && money_sim != ''){
      $('#accountreceivable_set-group').find('.add-row .add-debt').css('display', 'block');
      $('#accountreceivable_set-group').find('.add-row a').css('display', 'none');
    } else {
      $('#accountreceivable_set-group').find('.add-row a').css('display', 'block');
      $('#accountreceivable_set-group').find('.add-row .add-debt').css('display', 'none');
    }
   
    $('#accountreceivable_set-group').find('.add-row a').click(function(){
      var arr_status = [];
      $(`.dynamic-accountreceivable_set`).find('select[name^="accountreceivable_set"][name$="status"]').each(function(){
        if($(this).val() == 2){
          arr_status.push($(this).val())
        }
      });
      var status_length = arr_status.length;
      var account_length = $('#accountreceivable_set-group').find('.dynamic-accountreceivable_set').length;
      if(account_length == 1 || (account_length - status_length == 1)){
        $(this).css('display', 'none');
        $('#accountreceivable_set-group').find('.add-row .add-debt').css('display', 'block')
      }
    })
  });

  $(document).on("change keyup input keypress", ".dynamic-accountreceivable_set input[name^='accountreceivable_set'][name$='amount_payment']", function (e) {
    var column_index = $(this).closest('tbody').find("input[name^='accountreceivable_set'][name$='amount_payment']").index(this);
    var amount_payment = 0;
    var money_sim = $("[name='amount']").val();
    amount_payment = sum_Column_Amount('', '.field-amount_payment');

    if(Number(amount_payment) > Number(money_sim)){
      e.preventDefault();
    }
    change_amount_customer('', column_index);
  });

  $(document).on("change keyup input keypress", ".dynamic-accountreceivable_set input[name^='accountreceivable_set'][name$='amount_interest']", function (e) {
    get_Sum_Column('', '.field-amount_interest', '.sum_interest')
  });

  $(document).on("change focus", ".dynamic-accountreceivable_set input[name^='accountreceivable_set'][name$='created_userpay']", function () {
    var column_index = $(this).closest('tbody').find("input[name^='accountreceivable_set'][name$='created_userpay']").index(this);
   
    if(order_type ==installment && column_index>0){
      var date_now = $(this).val();
      var date_before = $(`.dynamic-accountreceivable_set`).find(`input[name='accountreceivable_set-${column_index - 1}-created_userpay']`).val();
      var field_iir = $('.field-iir').find('.txt_iir').text();
      var percent_iir = $("input[name='iir']").val();
      var start = new Date(date_now);
      var end = new Date(date_before);
      var diffDate = (start - end) / (1000 * 60 * 60 * 24);
      var days = Math.round(diffDate);

      var amount_remaining_before = $(`.dynamic-accountreceivable_set`).find(`input[name='accountreceivable_set-${column_index - 1}-amount_remaining']`).val();
     
      if(field_iir == percent){
        var amount_interest = Math.round(Number(amount_remaining_before)/(100*30))*days*Number(percent_iir)
      } else {
        var amount_interest = Math.round(days * Number(amount_remaining_before)*Number(percent_iir)/(Math.pow(10, 6)))
      }
      $(`.dynamic-accountreceivable_set`).find(`input[name^='accountreceivable_set-${column_index}-amount_interest']`).val(amount_interest);

      //tính tổng tiền lãi với sim trả góp
      get_Sum_Column('', '.field-amount_interest', '.sum_interest');

      //tính tổng lãi tạm tính với sim trả góp
      get_Sum_Column('', '.field-amount_interest_temp', '.sum_interest_temp');
    }
  });

  $(document).on("change", ".dynamic-accountreceivable_set select[name^='accountreceivable_set'][name$='status']", function () {
    var col_index = $(this).closest('tbody').find("select[name^='accountreceivable_set'][name$='status']").index(this);
    var col_value = $(this).val();
    var input_payment = $(`.dynamic-accountreceivable_set`).find(`input[name^='accountreceivable_set-${col_index}-amount_payment']`).val();
    disable_column_data('', col_index, col_value);
    var money_sim = $("[name='amount']").val();
    format_sim = money_sim.replace(/([^0-9])/g,"");
    var amount_payment = sum_Column_Amount('', '.field-amount_payment');
    if($(this).val() == 2 && input_payment != '' && Number(amount_payment) < Number(money_sim)){
      $('#accountreceivable_set-group').find('.add-row a').css('display', 'block');
      $('#accountreceivable_set-group').find('.add-row .add-debt').css('display', 'none');
    } else {
      $('#accountreceivable_set-group').find('.add-row a').css('display', 'none');
      $('#accountreceivable_set-group').find('.add-row .add-debt').css('display', 'block');
    }

    if($(this).val() == 2 && input_payment != ''){
      $(`#accountreceivable_set-${col_index}`).find('.delete').css('visibility', 'hidden');
    } else {
      $(`#accountreceivable_set-${col_index}`).find('.delete').css('visibility', 'visible');
    }
  });

  //click button delete update count
  $(document).on("click", ".dynamic-accountreceivable_set .inline-deletelink", function () {
    var account_length = $('#accountreceivable_set-group').find('.dynamic-accountreceivable_set').length;
    if(account_length == 0){
      $('#accountreceivable_set-group').find('.add-row a').css('display', 'block');
      $('#accountreceivable_set-group').find('.add-row .add-debt').css('display', 'none')
    }
    sum_amount_payment("");
  });

  //công nợ thợ
  if(store_type != kho_sim){
    $('#accountreceivable_set-2-empty').after(
      '<tr>' +
          '<td></td>' +
          '<td>Tổng cộng</td>' +
          '<td></td>' +
          '<td></td>' +
          `<td class="sum_amount_customer-2" style="text-align: center;"></td>` +
          '<td class="sum_remain_customer-2" style="text-align: center;"></td>' +
          '<td></td>' +
          '<td></td>' +
          '<td></td>' +
          '<td></td>' +
          '<td></td>' +
      '</tr>'
    )
  }
  $(document).ready(function() {
    //tính tổng
    if(store_type != kho_sim){
      sum_amount_payment('-2')
      //set action readonly status money
      $(`.dynamic-accountreceivable_set-2`).find(`select[name^='accountreceivable_set-2'][name$='status']`).each(function(){
        var col_index = $(this).closest('tbody').find(`select[name^='accountreceivable_set-2'][name$='status']`).index(this);
        var col_value = $(this).val();
        disable_column_data('-2', col_index, col_value);
      })
      $('#accountreceivable_set-2-group').find('.add-row td').append('<span class="add-debt">Thêm một Công nợ KH </span>');
      var money_sim = $("[name='pg']").val();
      var amount_payment = sum_Column_Amount('-2', '.field-amount_payment');
      if(Number(amount_payment)>=Number(money_sim) && money_sim != ''){
        $('#accountreceivable_set-2-group').find('.add-row .add-debt').css('display', 'block');
        $('#accountreceivable_set-2-group').find('.add-row a').css('display', 'none');
      } else {
        $('#accountreceivable_set-2-group').find('.add-row a').css('display', 'block');
        $('#accountreceivable_set-2-group').find('.add-row .add-debt').css('display', 'none');
      }
   
      $('#accountreceivable_set-2-group').find('.add-row a').click(function(){
        var arr_status = [];
        $(`.dynamic-accountreceivable_set-2`).find('select[name^="accountreceivable_set-2"][name$="status"]').each(function(){
          if($(this).val() == 2){
            arr_status.push($(this).val())
          }
        });
        var status_length = arr_status.length;
        var account_length = $('#accountreceivable_set-2-group').find('.dynamic-accountreceivable_set-2').length;
        if(account_length == 1 || (account_length - status_length == 1)){
          $(this).css('display', 'none');
          $('#accountreceivable_set-2-group').find('.add-row .add-debt').css('display', 'block')
        }
      })
    }
  });

  $(document).on("change keyup input keypress", ".dynamic-accountreceivable_set-2 input[name^='accountreceivable_set-2'][name$='amount_payment']", function (e) {
    var column_index = $(this).closest('tbody').find("input[name^='accountreceivable_set'][name$='amount_payment']").index(this);
    var amount_payment = 0;
    var money_sim = $("[name='pg']").val();
    amount_payment = sum_Column_Amount('-2', '.field-amount_payment');
    
    if(Number(amount_payment) > Number(money_sim)){
      $(`#accountreceivable_set-2-group`).find('.add-row a').css('display', 'none');
      $(`#accountreceivable_set-2-group`).find('.add-row .add-debt').css('display', 'block')
      e.preventDefault();
    }
    change_amount_customer('-2', column_index);
  });

  $(document).on("change", ".dynamic-accountreceivable_set-2 select[name^='accountreceivable_set-2'][name$='status']", function () {
    var col_index = $(this).closest('tbody').find("select[name^='accountreceivable_set-2'][name$='status']").index(this);
    var col_value = this.value;
    var money_sim = $("[name='pg']").val();
    amount_payment = sum_Column_Amount('-2', '.field-amount_payment');
    disable_column_data('-2', col_index, col_value);

    var input_payment = $(`.dynamic-accountreceivable_set-2`).find(`input[name^='accountreceivable_set-2-${col_index}-amount_payment']`).val();
   
    if($(this).val() == 2 && input_payment != '' && Number(amount_payment) < Number(money_sim)){
      $('#accountreceivable_set-2-group').find('.add-row a').css('display', 'block');
      $('#accountreceivable_set-2-group').find('.add-row .add-debt').css('display', 'none')
      $(`#accountreceivable_set-2-${col_index}`).find('.delete').css('visibility', 'hidden');
    } else {
      $('#accountreceivable_set-2-group').find('.add-row a').css('display', 'none');
      $('#accountreceivable_set-2-group').find('.add-row .add-debt').css('display', 'block')
      

    if($(this).val() == 2 && input_payment != ''){
      $(`#accountreceivable_set-2-${col_index}`).find('.delete').css('visibility', 'hidden');
    } else {
      $(`#accountreceivable_set-2-${col_index}`).find('.delete').css('visibility', 'visible');
      }
    }
  });

  //click button delete update count
  $(document).on("click", ".dynamic-accountreceivable_set-2 .inline-deletelink", function () {
    var account_length = $('#accountreceivable_set-2-group').find('.dynamic-accountreceivable_set-2').length;
    if(account_length == 0){
      $('#accountreceivable_set-2-group').find('.add-row a').css('display', 'block');
      $('#accountreceivable_set-2-group').find('.add-row .add-debt').css('display', 'none')
    }
    sum_amount_payment("-2");
  });

  $(document).on("change", "input[type=radio][name=installment_type]", function () {
    var txt_type = $(this).val();
    if(txt_type == percent){
      $('#id_iir_helptext').find('.txt_iir').text('% / tháng');
    } else {
      $('#id_iir_helptext').find('.txt_iir').text('đồng / triệu');
    }
  });

  //set disable when status='đã thanh toán'
function disable_column_data(type, col_index, col_value){
  if(col_value == '2'){
    $(`.dynamic-accountreceivable_set${type}`).find(`input[name^='accountreceivable_set${type}-${col_index}-amount_payment']`).attr("readonly",true);
    $(`.dynamic-accountreceivable_set${type}`).find(`input[name^='accountreceivable_set${type}-${col_index}-created_userpay']`).attr("readonly",true);
    $(`.dynamic-accountreceivable_set${type}`).find(`select[name^='accountreceivable_set${type}-${col_index}-method_pay']`).find("option").prop("hidden", true);
    $(`.dynamic-accountreceivable_set${type}`).find(`select[name^='accountreceivable_set${type}-${col_index}-method_pay']`).css({'background-color' : '#f8f8f8', 'color': '#868889', 'cursor' : 'not-allowed' });
    $(`.dynamic-accountreceivable_set${type}`).find(`input[name^='accountreceivable_set${type}-${col_index}-user_create']`).attr("readonly",true);
    $(`.dynamic-accountreceivable_set${type}`).find(`input[name^='accountreceivable_set${type}-${col_index}-created_at']`).attr("readonly",true);
    $(`.dynamic-accountreceivable_set${type}`).find(`input[name^='accountreceivable_set${type}-${col_index}-type']`).attr("readonly",true);
    $(`.dynamic-accountreceivable_set${type}`).find(`textarea[name^='accountreceivable_set${type}-${col_index}-comment']`).attr("readonly",true);
    if(order_type == installment){
      $(`.dynamic-accountreceivable_set${type}`).find(`input[name^='accountreceivable_set${type}-${col_index}-amount_interest']`).attr("readonly",true);
    }
  } else {
    $(`.dynamic-accountreceivable_set${type}`).find(`input[name^='accountreceivable_set${type}-${col_index}-amount_payment']`).attr("readonly",false);
    $(`.dynamic-accountreceivable_set${type}`).find(`input[name^='accountreceivable_set${type}-${col_index}-created_userpay']`).attr("readonly",false);
    $(`.dynamic-accountreceivable_set${type}`).find(`select[name^='accountreceivable_set${type}-${col_index}-method_pay']`).find("option").prop("hidden", false);
    $(`.dynamic-accountreceivable_set${type}`).find(`select[name^='accountreceivable_set${type}-${col_index}-method_pay']`).css({'background-color' : '#fff', 'color': '#333', 'cursor' : 'pointer' })
    $(`.dynamic-accountreceivable_set${type}`).find(`input[name^='accountreceivable_set${type}-${col_index}-user_create']`).attr("readonly",false);
    $(`.dynamic-accountreceivable_set${type}`).find(`input[name^='accountreceivable_set${type}-${col_index}-created_at']`).attr("readonly",false);
    $(`.dynamic-accountreceivable_set${type}`).find(`input[name^='accountreceivable_set${type}-${col_index}-type']`).attr("readonly",false);
    $(`.dynamic-accountreceivable_set${type}`).find(`textarea[name^='accountreceivable_set${type}-${col_index}-comment']`).attr("readonly",false);
    if(order_type == installment){
      $(`.dynamic-accountreceivable_set${type}`).find(`input[name^='accountreceivable_set${type}-${col_index}-amount_interest']`).attr("readonly",false);
    }
  }
}
//tính tổng công nợ
function sum_amount_payment(type){
  //tổng số tiên
  get_Sum_Column(type, '.field-amount_payment', `.sum_amount_customer${type}`);

  //tổng gốc còn lại
  get_Sum_Column(type, '.field-amount_remaining', `.sum_remain_customer${type}`);

  var order_type = $('.field-order_type').find('.readonly').text();
  if(order_type == installment && type == ''){
    get_Sum_Column(type, '.field-amount_interest', `.sum_interest${type}`);

    get_Sum_Column(type, '.field-amount_interest_temp', `.sum_interest_temp${type}`);
  }
}
//tính tổng công nợ khi thay đổi input
function change_amount_customer(type, column_index){
  var amount_payment = 0;
  amount_payment = sum_Column_Amount(type, '.field-amount_payment')
  var amount_sim = $("[name='amount']").val();
  var format_amount = amount_sim.replace(/([^0-9])/g,"");
  var pg = $("[name='pg']").val();
  if(type == '-2' && store_type == kho_appsim){
    var item_amount = Number(pg) - Number(amount_payment);
  } else {
    var item_amount = Number(format_amount) - Number(amount_payment);
  }
  $(`.dynamic-accountreceivable_set${type}`).find(`input[name='accountreceivable_set${type}-${column_index}-amount_remaining']`).val(item_amount);
  var order = $('.field-order_type').find('.readonly').text();
  if(Number(amount_payment) > Number(format_amount) && order == 'Đơn thường' && type == ''){
    $('select[name="pay_kh_status"]').val(2).change();
  } else {
    $('select[name="pay_kh_status"]').val('').change();
  }
  get_Sum_Column(type, '.field-amount_payment', `.sum_amount_customer${type}`);

  get_Sum_Column(type, '.field-amount_remaining', `.sum_remain_customer${type}`);
}

function get_Sum_Column(type, element, sum_text){
  var sum = sum_Column_Amount(type, element);
  var txt_sum = document.querySelector(sum_text);
  var format_sum = `${sum}`.replace(/\D/g, "").replace(/\B(?=(\d{3})+(?!\d)\.?)/g, ".");
  if(txt_sum){
    txt_sum.innerHTML = `${format_sum} đ`
  }
}

function sum_Column_Amount(type, col_element){
  var group_item = document.querySelectorAll(`#accountreceivable_set${type}-group .dynamic-accountreceivable_set${type}`);
  var sum_amount = 0;
  if(group_item.length > 0){
    group_item.forEach(element => {
      var row_item = element.querySelector(col_element);
      sum_amount += Number(row_item.children[0].value);
    })
  }
  return sum_amount;
}
})