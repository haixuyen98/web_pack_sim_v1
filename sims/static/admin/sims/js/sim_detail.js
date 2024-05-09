document.addEventListener("DOMContentLoaded", function() {
    const simInput = document.getElementById("id_sim");
    const priceField = document.getElementById("id_amount");
    const storeTypeField = document.getElementById("id_store_type");
    const searchButton = document.getElementById("search_sim");
  
    if (simInput && searchButton) {
        searchButton.style.display = "block";
        searchButton.style.marginLeft = "10px"; // Adjust the margin as needed
        simInput.parentNode.insertBefore(searchButton, simInput.nextSibling);
    } else {
        searchButton.style.display = "none";
    }
  
    if (simInput && searchButton) {
        searchButton.addEventListener("click", function(event) {
          event.preventDefault();
            const simValue = simInput.value;
            // Make AJAX request to fetch SIM details
            fetch(`/admin/sims/simorder/get-detail-sim-store/${simValue}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}',
                },
            }).then(response => {
                $('#sim-value-error').remove();
                if (response.ok) {
                    return response.json()
                } else {
                    $('.field-sim .flex-container').before(`<ul id="sim-value-error" class="errorlist"><li>Sim không tồn tại. Vui lòng thêm số "${simValue}" vào kho trước khi tạo đơn.</li></ul>`);
                }
            }).then(data => {
                // Update amount fields with retrieved information
                priceField.value = data.simDetail.pb;
                storeTypeField.value = data.simDetail.store_type
                $('.field-telco_id').find('.readonly').html(data.simDetail.telcoText);
                $('.field-c2').find('.readonly').html(data.simDetail.categoryText);
                $("#btn-check-kho").html(data.template_kho);
                if(data.simDetail.c[0] == 200){
                    if($('field-percentUpfront').length == 0){
                        $('.field-amount').after('<div class="form-row field-percentUpfront">'+
                                                    '<div>'+
                                                        '<div class="flex-container">'+
                                                            '<label for="id_percentUpfront">'+
                                                                'Dự tính trả trước:'+
                                                            '</label>'+
                                                            '<input id="id_percentUpfront" name="percentUpfront" required="" step="1" type="number" value="0">'+
                                                        '</div>'+
                                                    '</div>'+
                                                '</div>');
                    }
                    if($('.field-monthNumber').length == 0){
                        $('.field-percentUpfront').after('<div class="form-row field-monthNumber">'+
                            '<div>'+
                                '<div class="flex-container">'+
                                    '<label for="id_monthNumber">'+
                                        'Số tháng trả lãi:'+
                                    '</label>'+
                                    '<input id="id_monthNumber" name="monthNumber" required="" step="1" type="number" value="0">'+
                                '</div>'+
                            '</div>'+
                        '</div>');
                    }
                    if($('.field-installment_type').length == 0){
                        $('.field-monthNumber').after('<div class="form-row field-installment_type">'+
                            '<div>'+
                                '<div class="flex-container">'+
                                    '<label for="id_monthNumber">'+
                                        'Chọn đơn vị lãi suất:'+
                                    '</label>'+
                                    '<div id="id_installment_type">'+
                                        '<div>'+
                                            '<label for="id_installment_type_0">'+
                                                '<input id="id_installment_type_0" name="installment_type" type="radio" value="1">'+' % / tháng'+
                                            '</label>'+
                                        '</div>'+
                                        '<div>'+
                                            '<label for="id_installment_type_0">'+
                                                '<input id="id_installment_type_1" name="installment_type" type="radio" value="2">'+' đồng / triệu'+
                                            '</label>'+
                                        '</div>'+
                                    '</div>'+
                                '</div>'+
                            '</div>'+
                        '</div>');
                    }
                    if($('.field-iir').length == 0){
                        $('.field-installment_type').after('<div class="form-row field-iir">'+
                            '<div>'+
                                '<div class="flex-container">'+
                                    '<label for="id_iir">'+
                                        'Lãi suất:'+
                                    '</label>'+
                                    '<input id="id_iir" name="iir" type="text" value="0">'+
                                '</div>'+
                                '<div class="help" id="id_iir_helptext">'+
                                    '<div>'+
                                        '<span class="txt_iir">'+
                                            'đồng / triệu'+
                                        '</span>'+
                                    '</div>'+
                                '</div>'+
                            ' </div>'+
                        '</div>');
                    }
                } else {
                    $('.field-iir').remove();
                    $('.field-percentUpfront').remove();
                    $('.field-monthNumber').remove();
                    $('.field-installment_type').remove();
                }
            })
            .catch(error => console.error("Error fetching SIM details:", error));
        });
    }
  
    var errorNote = document.querySelector('.errornote');
    if (errorNote) {
        errorNote.textContent = "Vui lòng sửa lỗi dưới đây";
    }
  
    var anchors = document.querySelectorAll('a.addlink');
    anchors.forEach(function(anchor) {
        var content = anchor.innerHTML || anchor.innerText;
        if (content.includes("Thêm vào")) {
            content = content.replace("Thêm vào", "Tạo mới");
            anchor.innerHTML = content;
        }
    });
    var historyLink = document.querySelectorAll('.historylink');
    historyLink.forEach(function(history) {
      historyLink[0].style.display = "None";
      history.innerHTML = "Lịch sử thay đổi";
    })
  });