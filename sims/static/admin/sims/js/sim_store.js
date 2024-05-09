const pack = {
  "Trả Trước": ["1", "tra truoc", "tratruoc", "tt", "sim tra truoc", "simtratruoc"],
  "Trả Sau": ["2", "tra sau", "trasau", "ts", "sim tra sau", "simtrasau"],
};

const homeNetwork = {
  Viettel: [
    "viettel",
    "vietel",
    "vietell",
    "viettell",
    "vieten",
    "vietten",
    "viet ten",
    "viet theo",
    "vt",
    "viettheo",
  ],
  Vinaphone: ["vinaphone", "vina", "vn", "vnp"],
  Mobifone: ["mobiphone", "mobifone", "mobi", "mobile", "mb", "mbf", "mbp"],
  Vietnamobile: ["vietnamobile", "vietnammobile", "vietnam", "vnmb"],
  Gmobile: ["gmobile", "gmobi"],
  Itel: ["iteltelecom", "itelecom", "itel", "itel", "jtel"],
  Wintel: ["redi", "redy", "reddy", "wintel", "winten", "winttel"],
  "Máy bàn": ["may ban", "mayban", "máy bàn"],
};

const DEFAULT_NUMBER_PREFIX = {
  "VIETTEL": ["086", "096", "097", "098", "039", "038", "037", "036", "035", "034", "033", "032"],
  "VINAPHONE": ["091", "094", "088", "083", "084", "085", "081", "082"],
  "MOBIPHONE": ["070", "079", "077", "076", "078", "089", "090", "093"],
  "VIETNAMMOBILE": ["092", "052", "056", "058"],
  "GMOBILE": ["099","059"],
  "ITEL": ["087"],
  "WINTEL": ["055"],
  "DESKTOP_PHONE": ["0282","0283","0286","0287","0289","0242","0243","0246","0247","0248","0249","0212","0213","0214","0215","0216","0218","0203","0204","0205","0206","0207","0208","0209","0210","0219","0211","0220","0221","0222","0225","0226","0227","0228","0229","0232","0233","0234","0237","0238","0239","0235","0236","0252","0255","0256","0257","0258","0259","0260","0261","0262","0263","0269","0251","0254","0271","0274","0276","0270","0272","0273","0275","0277","0290","0291","0292","0293","0294","0296","0297","0299"]
};

function getTelWithPrefix(phone) {
  if (DEFAULT_NUMBER_PREFIX['VIETTEL'].includes(phone.slice(0, 3))) {
      return 'Viettel';
  }
  if (DEFAULT_NUMBER_PREFIX['VINAPHONE'].includes(phone.slice(0, 3))) {
      return 'Vinaphone';
  }
  if (DEFAULT_NUMBER_PREFIX['MOBIPHONE'].includes(phone.slice(0, 3))) {
      return 'Mobifone';
  }
  if (DEFAULT_NUMBER_PREFIX['VIETNAMMOBILE'].includes(phone.slice(0, 3))) {
      return 'Vietnamobile';
  }
  if (DEFAULT_NUMBER_PREFIX['GMOBILE'].includes(phone.slice(0, 3))) {
      return 'Gmobile';
  }
  if (DEFAULT_NUMBER_PREFIX['ITEL'].includes(phone.slice(0, 3))) {
      return 'Itel';
  }
  if (DEFAULT_NUMBER_PREFIX['WINTEL'].includes(phone.slice(0, 3))) {
      return 'Wintel';
  }
  if (DEFAULT_NUMBER_PREFIX['DESKTOP_PHONE'].includes(phone.slice(0, 4))) {
      return 'Máy bàn';
  }
  return null;
}

function checkHomeNetWork(t, homeNetwork) {
  if (!t) {
    return true;
  }
  for (const [key, value] of Object.entries(homeNetwork)) {
    if (value.includes(stringToSlug(t.toLowerCase()))) return true;
  }
  return false;
}

function toggleSelectInstallment(checkbox) {
  const installment = document.querySelector(".toggle-installment");
  if (!checkbox.checked) {
    installment.style.display = "none";
  } else {
    installment.style.display = "block";
  }
}

function toggleSelectInstallmentType(checkbox) {
  const installmentPercent = document.querySelector(".installment-percent");
  const installmentVnd = document.querySelector(".installment-vnd");
  if (!checkbox.checked) {
    installmentPercent.style.display = "block";
    installmentVnd.style.display = "none";
  } else {
    installmentPercent.style.display = "none";
    installmentVnd.style.display = "block";
  }
}

function toggleSelectCategory(checkbox) {
  const toggleCate = document.querySelector(".toggle-category");
  if (!checkbox.checked) {
    toggleCate.style.display = "none";
  } else {
    toggleCate.style.display = "block";
    var selections = document.querySelectorAll(".selection");
    selections.forEach(function (selection) {
      var arrowDiv = document.createElement("div");
      arrowDiv.classList.add("select2-dropdown-arrow");
      selection.appendChild(arrowDiv);
    });
  }
}

function stringToSlug(str) {
  var from =
      "àáãảạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệđùúủũụưừứửữựòóỏõọôồốổỗộơờớởỡợìíỉĩịäëïîöüûñçýỳỹỵỷ",
    to =
      "aaaaaaaaaaaaaaaaaeeeeeeeeeeeduuuuuuuuuuuoooooooooooooooooiiiiiaeiiouuncyyyyy";
  for (var i = 0, l = from.length; i < l; i++) {
    str = str.replace(RegExp(from[i], "gi"), to[i]);
  }
  return str;
}

function formattedHomeNetWork(t, homeNetwork) {
  if (!t) {
    return {
      t,
      homeNetworkValid: true,
    };
  }
  for (const [key, value] of Object.entries(homeNetwork)) {
    if (value.includes(stringToSlug(t.toLowerCase()))) {
      return {
        t: key,
        homeNetworkValid: true,
      };
    }
  }
  return {
    t,
    homeNetworkValid: false,
  };
}

function formattedPack(tt, pack) {
  if (!tt) {
    return {
      tt,
      packValid: true,
    };
  }
  for (const [key, value] of Object.entries(pack)) {
    if (tt) {
      if (value.includes(stringToSlug(tt.toLowerCase()))) {
        return {
          tt: key,
          packValid: true,
        };
      }
    }
  }
  return {
    tt,
    packValid: false,
  };
}

function checkPhone(phone) {
  const regexPhoneNumber = /(0[2|3|5|7|8|9])+([0-9]{8,9})\b/g;
  return phone.replace(/\./g, "").match(regexPhoneNumber);
}

function checkPrice(price) {
  const regexPrice = /^[\d.,]+$/;
  return price.match(regexPrice);
}

function checkPack(tt, pack) {
  if (!tt) return true;
  for (const [key, value] of Object.entries(pack)) {
    if (value.includes(stringToSlug(tt.toLowerCase()))) return true;
  }
  return false;
}

function formatCurrency(number) {
  // Chuyển số thành chuỗi và đảo ngược chuỗi để dễ xử lý
  const numberStr = number.replace(/[.,]/g, "").split("").reverse().join("");

  // Thêm dấu phẩy sau mỗi 3 chữ số
  let formattedStr = numberStr.match(/.{1,3}/g).join(",");

  // Đảo ngược lại chuỗi để có định dạng đúng
  formattedStr = formattedStr.split("").reverse().join("");

  return formattedStr;
}

function getCheckedRadioValue() {
  const radioButtons = document.getElementsByName("exchange_rate");

  for (let i = 0; i < radioButtons.length; i++) {
    if (radioButtons[i].checked) {
      return radioButtons[i].value;
    }
  }

  return "1";
}

function showDataCheckKho(url) {
  var dataContainer = document.createElement("div");
  dataContainer.setAttribute("id", "data_check_kho");
  var btnCheckKho = document.getElementById("btn-check-kho");
  if (document.getElementById("data_check_kho") == null) {
    btnCheckKho.appendChild(dataContainer);
    var dataContent = document.createElement("iframe");
    dataContent.setAttribute("src", url);
    dataContent.setAttribute("class", "popup_check_kho");
    dataContent.setAttribute("style", "width: 100%;");
    // Append the modal content to the modal container
    dataContainer.appendChild(dataContent);
  }
}

function showTable(body) {
  const { data, selectedValue, page } = body;
  $(".table-data").removeClass("hidden");
  const tbody = document.getElementById("contentTable");
  tbody.innerHTML = "";
  const startIndex = (page - 1) * rowsPerPage;
  const endIndex = startIndex + rowsPerPage;
  const paginatedData = data.slice(startIndex, endIndex);
  for (let i = 0; i < paginatedData.length; i++) {
    // Tạo một dòng
    const row = document.createElement("tr");
    const { isError, simData, duplicate } = paginatedData[i];
    if (isError || duplicate) {
      row.classList.add("highlighted");
    }
    // Thêm ô STT
    const sttCell = document.createElement("td");
    sttCell.textContent = i + 1; // Số thứ tự bắt đầu từ 1
    row.appendChild(sttCell);

    // Thêm các ô dữ liệu từ mảng
    for (let j = 0; j < simData.length; j++) {
      const cell = document.createElement("td");

      if (j == 3 && simData[0] && !isError) {
        if (simData[j] && simData[j] !== getTelWithPrefix(simData[0])) {
          cell.textContent = simData[j] + " (CMGS)"
        } else {
          cell.textContent = getTelWithPrefix(simData[0])
        }
      } else if (j == 1 && selectedValue && !isError) {
        cell.textContent = formatCurrency(simData[j] + selectedValue.slice(1));
      } else {
        cell.textContent = simData[j];
      }
      row.appendChild(cell);
    }

    // Thêm dòng vào tbody
    tbody.appendChild(row);
  }
  $(".pagination-controls").removeClass("hidden");
  updatePaginationControls(data.length, page);
}

function updatePaginationControls(totalItems, currentPage) {
  const totalPages = Math.ceil(totalItems / rowsPerPage);
  document.getElementById(
    "pagination-info"
  ).textContent = `Trang ${currentPage} / ${totalPages}`;
  document.getElementById("btn-prev").disabled = currentPage === 1;
  document.getElementById("btn-next").disabled = currentPage === totalPages;
}

function partition(arr, left, right, getKey, pivot) {
  while (left <= right) {
    while (getKey(arr[left]) < getKey(pivot)) {
      left++;
    }
    while (getKey(arr[right]) > getKey(pivot)) {
      right--;
    }
    if (left <= right) {
      [arr[left], arr[right]] = [arr[right], arr[left]];
      left++;
      right--;
    }
  }
  return left;
}

function quickSort(arr, left, right, getKey) {
  if (left >= right) return;

  let pivot = arr[Math.floor((left + right) / 2)];
  let index = partition(arr, left, right, getKey, pivot);

  quickSort(arr, left, index - 1, getKey);
  quickSort(arr, index, right, getKey);
}

let idCount = {};
let countError = 0;
let dataTable = [];
let currentPage = 1;
let rowsPerPage = 50;
let selectedValue = "1";
let uniqueIds = {};
let isModalOpen = false;

function formatData(dataJson) {
  dataJson.forEach((data) => {
    const dataStrings = data.map((val) => (val ? val + "" : ""));
    const id = dataStrings[0]
      ? !dataStrings[0].startsWith("0")
        ? "0" + dataStrings[0]
        : dataStrings[0]
      : "";
    const idNumber = id.replace(/\./g, "");
    const pn = dataStrings[1];
    const {tt, packValid} = formattedPack(dataStrings[2], pack);
    const {t, homeNetworkValid } = formattedHomeNetWork(dataStrings[3], homeNetwork);
    const note = dataStrings[4];
    if (id) {
      if (checkPhone(id)) {
        idCount[idNumber] = idCount[idNumber] ? idCount[idNumber] + 1 : 1;
      }
      if (
        !checkPhone(id) ||
        !checkPrice(pn) ||
        !homeNetworkValid ||
        !packValid
      ) {
        countError += 1;
        dataTable.push({
          isError: true,
          simData: dataStrings,
        });
      } else {
        if (idCount[idNumber] === 2) {
          countError += 2;
        } else if (idCount[idNumber] > 2) {
          countError += 1;
        }
        dataTable.push({
          isError: false,
          simData: [id, formatCurrency(pn), tt, t, note],
          id: idNumber,
          pn: BigInt(pn.replace(/[.,]/g, "")),
        });
      }
    }
  });

  quickSort(dataTable, 0, dataTable.length - 1, (item) => {
    if (item.isError) {
      return -Infinity;
    } else {
      const count = idCount[item.id];
      if (count && count > 1) {
        item.duplicate = true;
        return -count * 1000000 + Number(item.pn / BigInt(1000));
      }
      return -1;
    }
  });

  dataTable.slice(0, countError).forEach((item) => {
    if (!item.isError) {
      const itemId = item.id;
      const itemPn = item.pn;
      if (!uniqueIds[itemId] || uniqueIds[itemId].pn < itemPn) {
        uniqueIds[itemId] = item;
      }
    }
  });

  if (dataTable.length !== 0) {
    $(".table-data").addClass("hidden");
    if (dataTable.length - countError > 0) {
      $(".phones-valid").text(
        `${dataTable.length - countError} số đã sẵn sàng`
      );
    }
    if (countError > 0) {
      $(".phones-invalid").removeClass("hidden");
      $("#delete-sim-error").removeClass("hidden");
      $(".phones-invalid").text(`${countError} số không hợp lệ`);
    } else {
      $(".phones-invalid").addClass("hidden");
      $("#delete-sim-error").addClass("hidden");
    }
    showTable({
      data: dataTable,
      selectedValue,
      page: 1,
    });
  }

  return { dataTable, countError, idCount, uniqueIds };
}

function deleteSimsError() {
  $(".phones-invalid").addClass("hidden");
  $("#delete-sim-error").addClass("hidden");
  const dataUniqueIds = Object.values(uniqueIds).map((val) => ({
    ...val,
    duplicate: false,
  }));
  $(".phones-valid").text(
    `${dataTable.length - countError + dataUniqueIds.length} số đã sẵn sàng`
  );
  dataTable = [...dataUniqueIds, ...dataTable.slice(countError)];
  const totalItems = dataTable.length;
  showTable({
    data: dataTable,
    selectedValue,
    page: 1,
  });
  updatePaginationControls(totalItems, currentPage);
  countError = 0;
  uniqueIds = {};
}

function nextPage() {
  const totalItems = dataTable.length;
  if (currentPage * rowsPerPage < totalItems) {
    currentPage++;
    showTable({
      data: dataTable,
      selectedValue,
      page: currentPage,
    });
    updatePaginationControls(totalItems, currentPage);
  }
}

function prevPage() {
  if (currentPage > 1) {
    currentPage--;
    showTable({
      data: dataTable,
      selectedValue,
      page: currentPage,
    });
    updatePaginationControls(dataTable.length, currentPage);
  }
}

$(document).ready(function () {
  $(".cat-multiple").select2({
    placeholder: "Danh mục",
  });

  $(".installment_payment").select2({
    placeholder: "Chọn mức trả trước",
  });

  $(".installment_term").select2({
    placeholder: "Chọn kỳ hạn trả góp",
  });

  const exchangeRates = document.getElementsByName("exchange_rate");
  exchangeRates.forEach(function (radioButton) {
    radioButton.addEventListener("change", function () {
      selectedValue = this.value;
      showTable({
        data: dataTable,
        selectedValue,
        page: currentPage,
      });
    });
  });

  $("#form-table").submit(function (e) {
    if (countError > 0) {
      $.toast({
        heading: "Lỗi",
        text: "Vui lòng xóa những số sai định dạng",
        position: {
          top: 20,
          right: 80,
        },
        icon: "error",
      });
      e.preventDefault();
      return;
    }
    const trigger = document.getElementById("delete-table");
    if(trigger.checked && !isModalOpen) {
      toggleModal()
      e.preventDefault();
    }
    else {
      if(isModalOpen) {
        toggleModal()
      }
      $.LoadingOverlay("show");
      const jsonData = JSON.stringify(dataTable.map((val) => val.simData));
      document.getElementById("data_input").value = jsonData;
    }
  });

  const modal = document.querySelector(".modal");
  const closeButton = document.querySelector(".close-button");
  const cancelButton = document.querySelector('.cancel-button')

  function toggleModal() {
    modal.classList.toggle("show-modal");
    isModalOpen = !isModalOpen;
  }

  closeButton.addEventListener("click", function() {
    toggleModal();
    isModalOpen = false;
  });
  cancelButton.addEventListener("click", function() {
    toggleModal()
    isModalOpen = false;
  });
});
