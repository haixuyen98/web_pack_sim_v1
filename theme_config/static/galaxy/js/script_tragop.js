function formatMoney(amount) {
  if (typeof amount !== 'number') {
      return 'Vui lòng nhập một số';
  }

  const formatter = new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
  });

  return formatter.format(amount);
}
export function toolTragop(getIdForm, priceSim) {
  const checkIdForm = getIdForm;
  const getPriceSim = priceSim;
  
  let checkadata = getPriceSim;
    let phantramPay = "30";
    let numberMonth = "12";
    let tongtientamtinh = (checkadata * phantramPay) / 100;

    let sotienNo = checkadata - tongtientamtinh;
          let kyhan = Number(numberMonth);
          let tongtienmoithang =
            (sotienNo / kyhan) * (1 + ((kyhan + 1) * 0.03) / 2);
    let roundedValue = Math.ceil(tongtienmoithang / 1000) * 1000;
    let totalValuesItems = roundedValue;
    const updateTotalValuesItems = () => {
      const innerFormTragopDiv = document.getElementById(checkIdForm);
      if (innerFormTragopDiv) {
        const pElement = innerFormTragopDiv.querySelector("#totalValuesItems");
        if (pElement) {
          pElement.textContent = `${totalValuesItems}`;
        } else {
          console.log('Element with id "totalValuesItems" not found');
        }
      }
    };

    const updateTongTienTamtinh = () => {
      const tongtientamtinh = (checkadata * phantramPay) / 100;
      const innerFormTragopDiv = document.getElementById(checkIdForm);
      if (innerFormTragopDiv) {
        const pElement = innerFormTragopDiv.querySelector("#tongtientamtinh");
        
        if (pElement) {
          pElement.textContent = `${formatMoney(tongtientamtinh)}`;
        } else {
          console.log('element with id "tongtientamtinh" not fun');
        }
      }
    };
    const innerFormTragopDiv = document.getElementById(checkIdForm);
    if (innerFormTragopDiv) {
      innerFormTragopDiv.insertAdjacentHTML(
        "beforeend",
        `
            <div class="box_tratruoc">
              <p class="title_item_method_count">Trả trước: </p>
              <div id="percentageForm">
                  <label>
                      <input type="radio" name="percentage" value="20"> 20%
                  </label>
                  <label>
                      <input type="radio" checked name="percentage" value="30"> 30%
                  </label>
                  <label>
                      <input type="radio" name="percentage" value="50"> 50%
                  </label>
                  <label>
                      <input type="radio" name="percentage" value="70"> 70%
                  </label>
              </div>
            </div>
            <div class="box_laixuatmonth">
              <p class="title_item_method_count">Số tháng trả góp: </p>
                <div id="numberForm">
                <label>
                    <input type="radio" name="numberMonth" value="1"> 1
                </label>
                <label>
                    <input type="radio" name="numberMonth" value="2"> 2
                </label>
                <label>
                    <input type="radio" name="numberMonth" value="3"> 3
                </label>
                <label>
                    <input type="radio" name="numberMonth" value="6"> 6
                </label>
                <label>
                    <input type="radio" name="numberMonth" value="9"> 9
                </label>
                <label>
                    <input type="radio" checked name="numberMonth" value="12"> 12
                </label>
                <label>
                    <input type="radio" name="numberMonth" value="15"> 15
                </label>
                <label>
                    <input type="radio" name="numberMonth" value="18"> 18
                </label>
                <label>
                    <input type="radio" name="numberMonth" value="24"> 24
                </label>
              </div>
            </div>
            <div class="box_footer_count">
              <p>Số tiền trả trước tạm tính</p>
              <p id="tongtientamtinh">${formatMoney(tongtientamtinh)}</p>
            </div>
            <div class="box_footer_count">
              <p>Mỗi tháng tạm tính: </p>
              <p id="totalValuesItems">${formatMoney(totalValuesItems)}</p>
            </div>`
      );
      const percentageForm =
        innerFormTragopDiv.querySelector("#percentageForm");
      const numberForm = innerFormTragopDiv.querySelector("#numberForm");
      if (percentageForm && numberForm) {
        document.addEventListener("change", function (event) {
          if (percentageForm) {
            const checkedRadio = Array.from(
              percentageForm.querySelectorAll('input[type="radio"]')
            ).find((radio) => radio.checked);
            if (checkedRadio) {
              phantramPay = checkedRadio.value;
              updateTongTienTamtinh();
            } else {
              console.log("no radio button is checked in percentageForm");
            }
          }
          if (numberForm) {
            const checkedRadioTwo = Array.from(
              numberForm.querySelectorAll('input[type="radio"]')
            ).find((radio) => radio.checked);
            if (checkedRadioTwo) {
              numberMonth = checkedRadioTwo.value;
              tongtientamtinh = (checkadata * phantramPay) / 100;
              updateTongTienTamtinh();
            } else {
              console.log("No radio button is checked in numberForm");
            }
          } else {
            console.log("Forms not found");
          }
          let sotienNo = checkadata - tongtientamtinh;
          let kyhan = Number(numberMonth);
          let tongtienmoithang =
            (sotienNo / kyhan) * (1 + ((kyhan + 1) * 0.03) / 2);
          let roundedValue = Math.ceil(tongtienmoithang / 1000) * 1000;
          totalValuesItems = formatMoney(roundedValue);
          updateTotalValuesItems();
        });
      } else {
        console.log('bạn chưa thêm thẻ có id percentageForm vào web');
      }
    } else {
      console.log("Thẻ không tồn tại");
    }
}
